# ETHOnline 2021 Hackathon

For the ETHOnline 2021 Hackathon we develop a laye 2 alpha strategy in the form of a yield optimization engine running on layer 2 connecting different layer 2 systems together. Specifically, we focus in this hack on optimizing LPing in Curve pools on Polygon and Arbitrum.

## What does the code do?

At a summary level, the code does this:

  + Download all exchange events that occurred in the polygon (POL) and arbitrum (ARB) pools.
  + Compute the equivalent USD volume from those exchanges.
  + Compute the delta b/w POL and ARB to get an idea of where the current exchanges are most in volume.
  + Plot the distribution change over time including moments.

Based on this data we are building a yield optimizing bot.

### How to Run

Rename the config.cfg.example into "config.cfg", then put your moralis ID and run the various stepX<...>.py scripts one after the other and change inputs as needed.

## Developers

Prerequisites:

  + The scanner module included in the root repo is compiled for MacOS only right now. If you need it compiled for another OS, please reach out to Jesper.

How to run the code: Rename the config.cfg.example into "config.cfg", then put your moralis ID and run the various `stepX<...>.py` scripts one after the other and change inputs as needed. The first step is to download all the transactions. You will see a progress bar, but running this the first time might take a good amount of time to finish.

Reach out to Jesper on our Discord server at https://discord.gg/mC86ZysZ if you get stuck!

# What is Composable Finance?

We partnered with Composable Finance: https://www.composable.finance/
Composable Finance is a cross-chain and cross-layer interoperability platform. It serves as a hyper-liquidity infrastructure layer for DeFi assets, powered by Layer 2 Ethereum and Polkadot.

How? We used their Mosaic bridge (which in turn uses their SDK): https://mosaic.composable.finance

The lack of interoperability between multiple blockchains and layers creates fragmentation and disparity in the ecosystem. Developers are very restricted in what they can build with siloed infrastructures, and users are forced to navigate complicated and lengthy processes if they want to utilize multiple chains or layers.
Composable Finance is working on a suite of different products to establish cross-chain and cross-layer interoperability that will reduce the barriers for DeFi developers and remove the unnecessary complexity for the users.
Our development roadmap has two phases. In the first phase, we will focus on multi-layer (L2/L2) interoperability, bridging the gap between different Ethereum Layer 2 implementations and sidechains. In the second phase, we will launch our parachain, Picasso. It has been developed over several months to enable a complete DeFi ecosystem on Polkadot. This will be accomplished through a parachain with built-in, customizable pallets for each of the key DeFi primitives as well as those more advanced secondary and tertiary features, enabling the development of seamless, interoperable dApps.

We want to thank the development team at Composable for guidance and help and we greatly enjoyed using their groundbreaking technology!

## How to run the code

The flow follows the "stepX_<...>.py" files from getting the data to analyzing it.
Currently, the scanner is taken from the Advanced Blockchain Research Development Kit (RDK) and is compiled for Mac OS.
If you want it compiled for other platforms please reach out to the point of contact (listed below).

## Point of Contact

Any questions? Please reach out to jesper@advancedblockchain.com

## Authors

  + Jesper Kristensen | Advanced Blockchain
  + Jason Chai
  + Brendan
  + Liam Beckman
  + Tobe
