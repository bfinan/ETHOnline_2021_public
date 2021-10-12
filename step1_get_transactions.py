# -*- coding: utf-8 -*-
"""
A stateful event scanner for Ethereum-based blockchains using Web3.py.

With the stateful mechanism, you can do one batch scan or incremental scans,
where events are added wherever the scanner left off.

@author Jesper Kristensen | Composable Finance.
All Rights Reserved.
"""

from configparser import ConfigParser
import datetime
import json
import logging
import os
import time
from tqdm import tqdm
from web3 import Web3
from web3.datastructures import AttributeDict
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware
from scanner import JSONifiedState, EventScanner

logger = logging.getLogger(__name__)

# CURVE POOL DETAILS GO HERE:

DATAPATH = "data"

# =====================
# (***) This is the Curve pool on Polygon:
# this contract: https://polygon.curve.fi/atricrypto3/ running on Polygon, so need polygon node
POOL_ADDRESS = "0x92215849c439E1f8612b6646060B4E3E5ef822cC"
NODE_TO_USE = "pol_archive"  # see config.cfg
ABI_EXCHANGE = """[{"name":"TokenExchange","inputs":[{"name":"buyer","type":"address","indexed":true},{"name":"sold_id","type":"uint256","indexed":false},{"name":"tokens_sold","type":"uint256","indexed":false},{"name":"bought_id","type":"uint256","indexed":false},{"name":"tokens_bought","type":"uint256","indexed":false}],"anonymous":false,"type":"event"}]
"""
POA_CHAIN = True
FNAME = "pol_pool_exchanges"
# =====================

# # =====================
# # (***) This is the Curve pool on Arbitrum:
# # this contract: https://arbitrum.curve.fi/tricrypto/ running on Arbitrum, so need arb node
# POOL_ADDRESS = "0x960ea3e3C7FB317332d990873d354E18d7645590"
# NODE_TO_USE = "arb_mainnet"  # see config.cfg
# ABI_EXCHANGE = """[{"name":"TokenExchange","inputs":[{"name":"buyer","type":"address","indexed":true},{"name":"sold_id","type":"uint256","indexed":false},{"name":"tokens_sold","type":"uint256","indexed":false},{"name":"bought_id","type":"uint256","indexed":false},{"name":"tokens_bought","type":"uint256","indexed":false}],"anonymous":false,"type":"event"}]
# """
# POA_CHAIN = False
# FNAME = "arb_pool_exchanges"
# # =====================


class ExchangeJSONifiedState(JSONifiedState):
    """
    How to process the event we are looking for.

    Just implement the method "process_event":
        def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> str:
    """

    def process_event(self, block_when: datetime.datetime, event: AttributeDict) -> str:
        """
        We have found an event that satisfies the contract details we are looking for.
        Now, how do we parse it?

        Here, we implement this for the case of an exchange event in the Curve pool.
        """
        # Events are keyed by their transaction hash and log index
        # One transaction may contain multiple events
        # and each one of those gets their own log index

        # event_name = event.event # "Transfer"
        log_index = event.logIndex  # Log index within the block
        # transaction_index = event.transactionIndex  # Transaction index within the block
        txhash = event.transactionHash.hex()  # Transaction hash
        block_number = event.blockNumber

        # Convert exchange event to our internal format
        args = event["args"]
        exchange = {
            "buyer": args.buyer,
            "bought_id": args.bought_id,
            "sold_id": args.sold_id,
            "tokens_sold": args.tokens_sold,
            "tokens_bought": args.tokens_bought,
            "timestamp": block_when.isoformat(),
        }

        # Create empty dict as the block that contains all exchanges by txhash
        if block_number not in self.state["blocks"]:
            self.state["blocks"][block_number] = {}

        block = self.state["blocks"][block_number]
        if txhash not in block:
            # We have not yet recorded any transfers in this transaction
            # (One transaction may contain multiple events if executed by a smart contract).
            # Create a tx entry that contains all events by a log index
            self.state["blocks"][block_number][txhash] = {}

        # Record this exchange in our database
        self.state["blocks"][block_number][txhash][log_index] = exchange

        # Return a pointer that allows us to look up this event later if needed
        return f"{block_number}-{txhash}-{log_index}"


if __name__ == "__main__":

    def run():

        cfg = ConfigParser()
        cfg.read("config.cfg")

        api_url = cfg["NodeURLs"][NODE_TO_USE]

        # Enable logs to the stdout.
        # DEBUG is very verbose level
        logging.basicConfig(level=logging.INFO)
        provider = HTTPProvider(api_url)

        # Remove the default JSON-RPC retry middleware
        # as it correctly cannot handle eth_getLogs block range
        # throttle down.
        provider.middlewares.clear()

        web3 = Web3(provider)

        if POA_CHAIN:
            print("POA chain detected... modifying middleware")
            # see here why: https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
            web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            assert web3.clientVersion is not None

        # Prepare stub CURVE_POOL_CONTRACT contract object
        abi_exchange = json.loads(ABI_EXCHANGE)
        CURVE_POOL_CONTRACT_JUST_EXCHANGE_PART = web3.eth.contract(abi=abi_exchange)

        # Restore/create our persistent state
        state = ExchangeJSONifiedState(fname=os.path.join(DATAPATH, FNAME))
        state.restore()

        scanner = EventScanner(
            web3=web3,
            contract=CURVE_POOL_CONTRACT_JUST_EXCHANGE_PART,
            state=state,
            event_templates=[
                CURVE_POOL_CONTRACT_JUST_EXCHANGE_PART.events.TokenExchange
            ],  # just use the exchange part
            filters={"address": POOL_ADDRESS},
            # How many maximum blocks at the time we request from JSON-RPC
            # and we are unlikely to exceed the response size limit of the JSON-RPC server
            max_chunk_scan_size=10000,
        )

        # Assume we might have scanned the blocks all the way to the last Ethereum block
        # that mined a few seconds before the previous scan run ended.
        # Because there might have been a minor Etherueum chain reorganisations
        # since the last scan ended, we need to discard
        # the last few blocks from the previous scan results.
        chain_reorg_safety_blocks = 10
        scanner.delete_potentially_forked_block_data(
            state.get_last_scanned_block() - chain_reorg_safety_blocks
        )

        # Scan from [last block scanned] - [latest ethereum block]
        # Note that our chain reorg safety blocks cannot go negative
        start_block = max(state.get_last_scanned_block() - chain_reorg_safety_blocks, 0)
        end_block = scanner.get_suggested_scan_end_block()
        blocks_to_scan = end_block - start_block

        print(f"Scanning events from blocks {start_block} - {end_block}")

        # Render a progress bar in the console
        start = time.time()
        with tqdm(total=blocks_to_scan) as progress_bar:

            def _update_progress(
                start,
                end,
                current,
                current_block_timestamp,
                chunk_size,
                events_count,
                total_events_count,
            ):

                if current_block_timestamp:
                    formatted_time = current_block_timestamp.strftime("%d/%b/%Y")
                else:
                    formatted_time = "no block time available"

                progress_bar.set_description(
                    f"block: {current} ({formatted_time}) - {chunk_size}, events in batch: {events_count} (total: {total_events_count})"
                )
                progress_bar.update(chunk_size)

            # Run the scan
            result, total_chunks_scanned = scanner.scan(
                start_block, end_block, progress_callback=_update_progress
            )

        state.save()
        duration = time.time() - start
        print(
            f"Scanned total {len(result)} Exchange events, in {duration} seconds, total {total_chunks_scanned} chunk scans performed"
        )

    run()
