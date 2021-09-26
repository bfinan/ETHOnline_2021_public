# -*- coding: utf-8 -*-
"""

@author Jesper Kristensen | Composable Finance.
All Rights Reserved.
"""

import datetime
import json
import os
import pandas as pd
import pickle
from pycoingecko import CoinGeckoAPI
from ratelimit import limits, sleep_and_retry
from backoff import on_exception, expo
from tqdm import tqdm


# # ====== TODO: GENERALIZE THIS INTO THE COINS function
# # ARBITRUM
# # https://arbiscan.io/address/0x960ea3e3C7FB317332d990873d354E18d7645590#code
# TYPE = "ARB"
# FILE_TO_LOAD = "data/arb_pool_exchanges.json"
# # format: [(token address, token name (our internal name), coingecko api id, scaling factor from contract), ...]
# coins = [
#     ("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", "tether", "tether", 1000000000000),
#     ("0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", "WBTC", "wrapped-bitcoin", 10000000000),
#     ("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", "WETH", "weth", 1)
# ]
# FILENAME = "arb_post.pkl"
# PRECISION = 10 ** 18
# # =========================


# =========================
# POLYGON
TYPE = "POL"
FILE_TO_LOAD = "data/pol_pool_exchanges.json"
coins = [
    ("0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171", "am3crv", "lp-3pool-curve", 1),
    ("0x5c2ed810328349100A66B82b78a1791B101C9D61", "WBTC", "wrapped-bitcoin", 10 ** 10),
    ("0x28424507fefb6f7f8E9D3860F56504E4e5f5f390", "amWETH", "aave-polygon-weth", 1),
]
FILENAME = "pol_post.pkl"
PRECISION = 10 ** 18
# =========================

print(f"RUNNING {TYPE}")


DATAPATH = "data"
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")  # for filename
FILENAME = (
    os.path.splitext(FILENAME)[0] + "_" + timestamp + os.path.splitext(FILENAME)[1]
)

with open(FILE_TO_LOAD, "r") as fd:
    data = json.load(fd)

blocks = data["blocks"]  # {<block ID>: <data>}

blockids = sorted(list(blocks.keys()))

# num API calls required
num_api_calls = 0
for blockid in blockids:
    blockdata = blocks[blockid]
    num_api_calls += len(blockdata)


@on_exception(expo, Exception, max_tries=8)
@limits(calls=50, period=60)
def get_price(token_name: str = None, date: str = None):
    # Let's rate-limit the API calls to coingecko (they limit at 50 calls per minute)
    cg = CoinGeckoAPI()
    price = cg.get_coin_history_by_id(id=token_name, date=date)["market_data"][
        "current_price"
    ]["usd"]
    return price


prices_already_seen = dict()  # cache our calls
volumes_by_date = dict()

total_usd_volume = 0
for i in tqdm(range(len(blockids))):
    blockid = blockids[i]
    blockdata = blocks[blockid]

    # from the contract: log TokenExchange(msg.sender, i, dx, j, dy)
    these_vols = 0
    for txhash in blockdata:
        txdatatmp = blockdata[txhash]
        logindex = list(txdatatmp.keys())[0]
        txdata = txdatatmp[logindex]

        token_exchanged = coins[txdata["sold_id"]][2]
        coin_precision = coins[txdata["sold_id"]][3]

        volume_exchanged = (
            txdata["tokens_sold"] * coin_precision / PRECISION
        )  # number of tokens exchanged
        date_exchanged = datetime.datetime.strptime(
            txdata["timestamp"], "%Y-%m-%dT%H:%M:%S"
        ).strftime("%d-%m-%Y")
        time_exchanged = datetime.datetime.strptime(
            txdata["timestamp"], "%Y-%m-%dT%H:%M:%S"
        ).strftime("%m-%d-%YT%H:%M:%S")

        # now get the USD value of it...
        # get the price on that date of the token

        token_price_usd = None
        if date_exchanged in prices_already_seen:
            if token_exchanged in prices_already_seen[date_exchanged]:
                token_price_usd = prices_already_seen[date_exchanged][token_exchanged]

        if token_price_usd is None:
            token_price_usd = get_price(token_name=token_exchanged, date=date_exchanged)

            if date_exchanged not in prices_already_seen:
                prices_already_seen[date_exchanged] = dict()
            if token_exchanged not in prices_already_seen[date_exchanged]:
                prices_already_seen[date_exchanged][token_exchanged] = dict()
            prices_already_seen[date_exchanged][token_exchanged] = token_price_usd

        # this is approximate since it's the close price of that day

        # token_price_usd = cg.get_price(ids=token_exchanged, vs_currencies='usd')[token_exchanged]["usd"]
        volume_usd = token_price_usd * volume_exchanged

        these_vols += volume_usd

        volumes_by_date[time_exchanged] = volume_usd

    total_usd_volume += these_vols

df = pd.DataFrame.from_dict(volumes_by_date, orient="index").sort_index()
df.rename({0: TYPE}, axis=1, inplace=True)

with open(os.path.join(DATAPATH, FILENAME), "wb") as fd:
    pickle.dump(df, fd)
