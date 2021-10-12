# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen | Composable Finance
All Rights Reserved
"""

import bisect
import os
import pickle
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==================
# FILE1 = "data/arb_vis_2021-09-24_22_57_19.pkl"
# FILE2 = "data/pol_vis_2021-09-24_23_23_50.pkl"

FILE1 = "data/arb_vis_2021-09-26_23_30_15.pkl"
FILE2 = "data/pol_vis_2021-09-26_23_10_09.pkl"
# ==================

# WE WILL COMPUTE (FILE1 - FILE2)

NAME1 = FILE1.split("/")[1].split("_")[0].upper()
NAME2 = FILE2.split("/")[1].split("_")[0].upper()

with open(FILE1, "rb") as fd:
    data1 = pickle.load(fd)

with open(FILE2, "rb") as fd:
    data2 = pickle.load(fd)

maxix = max(max(data1["x"]), max(data2["x"])) + 1

datas = [max(data1["x"]), max(data2["x"])]
maxaix = np.argmax(datas)

deltasxtime = np.array([data1, data2])[maxaix]["xtime"]
deltasx = list(range(maxix))
deltasy = np.zeros(maxix)


print(f"running {NAME1}...")
for x, y in zip(data1["x"], data1["y"]):
    deltasy[x] += y

print(f"running {NAME2}...")
for x, y in zip(data2["x"], data2["y"]):
    deltasy[x] -= y

firstix_not_zero = -1
for x, y in zip(deltasx, deltasy):
    if abs(y) > 0:
        firstix_not_zero = x
        break

# lastix_not_zero = -1
# for x, y in zip(deltasx[::-1], deltasy[::-1]):
#     if abs(y) > 0:
#         lastix_not_zero = x
#         break

print("done")

deltasx = deltasx[firstix_not_zero:]
deltasy = deltasy[firstix_not_zero:]
deltasxtime = deltasxtime[firstix_not_zero:]

print(f"first date = {min(deltasxtime)}")
print(f"last  date = {max(deltasxtime)}")

# plt.scatter(deltasxtime, deltasy / 1000, color="r", marker=".")
# plt.xlabel("time")
# plt.ylabel(f"exchange volume (in 1000s USD); positive: {NAME1} > {NAME2}")
# plt.grid()
#
# plt.xticks(rotation=45)
#
# plt.tight_layout()
# plt.savefig("volume_usd_delta.png", dpi=800, format="png")


# ========================================================
# ========================================================
#    COMPARE DISTRIBUTIONS
# ========================================================
# ========================================================
# Now plot the distribution for each as histogram and as they looked X days ago vs Y days ago etc.
# plot mean vs. time.
# plot skewness vs time.

df = pd.DataFrame(deltasy)

y = deltasy[abs(deltasy) > 0]
y = y[abs(y) < 2 * np.std(y)]

chunksize = 10000  # 1 day
separation = 10000  # 1 day
# plt.figure()
# plt.hist(y[-2*chunksize - separation:-chunksize - separation], bins=50, color="gray", alpha=0.6, label="$t_1$")
# assert len(y[-2*chunksize - separation:-chunksize - separation]) == chunksize
# plt.hist(y[-chunksize:], bins=50, color="b", alpha=0.4, label="$t_2>t_1$")
# assert len(y[-chunksize:]) == chunksize
# plt.grid()
# plt.axvline(0, linestyle="--", color="k")
# plt.legend(loc="best")
# plt.ylim(0, 1500)
# plt.title("LP Revenue Delta")
# plt.xlabel("ARB - POL revenue")
# plt.ylabel("counts")
# plt.show()

# plt.clf()
# plt.close()


# ========================================================
# ========================================================
#    CREATE MEAN AND SKEWNESS WINDOWS
# ========================================================
# ========================================================
# each datapoint is 10 seconds
windows_base = 4000
wdelta = 1000
maxwindow = 4100

store_here = "results"

# if not os.path.isdir(store_here):
#     os.makedirs(store_here)
#
# window = windows_base
# while window < maxwindow:
#
#     print(f"running window {window}...")
#
#     rollmean = df.rolling(window=window).mean()
#     rollskew = df.rolling(window=window).skew()
#
#     fig = plt.figure()
#     # sns.histplot(deltasy)
#     plt.subplot(121)
#     plt.plot(rollmean, label="mean", linewidth=0)
#
#     rollmeanpos = rollmean[rollmean > 0]
#     plt.fill_between(np.arange(len(rollmeanpos)), y1=rollmeanpos.values.flatten(), y2=0, color="purple", alpha=0.4, label="ARB")
#
#     rollmeanneg = rollmean[rollmean < 0]
#     plt.fill_between(np.arange(len(rollmeanneg)), y1=rollmeanneg.values.flatten(), y2=0, color="b", alpha=0.4, label="POL")
#
#     plt.ylabel("USD")
#     plt.grid()
#     plt.axhline(0, linestyle="--", color="k")
#     plt.legend(loc="best")
#
#     plt.subplot(122)
#     plt.plot(rollskew, label="skewness", linewidth=0)
#
#     rollskewpos = rollskew[rollskew > 0]
#     plt.fill_between(np.arange(len(rollskewpos)), y1=rollskewpos.values.flatten(), y2=0, color="purple", alpha=0.4, label="ARB")
#
#     rollskewneg = rollskew[rollskew < 0]
#     plt.fill_between(np.arange(len(rollskewneg)), y1=rollskewneg.values.flatten(), y2=0, color="b", alpha=0.4,
#                      label="POL")
#
#     plt.axhline(0, linestyle="--", color="k")
#     plt.grid()
#     plt.legend(loc="best")
#
#     fig.add_subplot(111, frameon=False)
#     # hide tick and tick label of the big axis
#     plt.tick_params(
#         labelcolor="none", which="both", top=False, bottom=False, left=False, right=False
#     )
#     plt.xlabel("time index")
#
#     plt.suptitle("(ARB - POL) Revenue Comparison")
#     plt.savefig(os.path.join(store_here, f"window_{window}.png"), format="png")
#     plt.clf()
#     plt.close()
#
#     window += wdelta


# =========================================================================================
# =========================================================================================
#     SIMULATE STATUS QUO INVESTOR AND PLOT THE RETURN VS PERCENT ALLOCATION
# =========================================================================================
# =========================================================================================
ARB_TVL = 37772775
# POL_TVL = 2561444  # atricrypto
POL_TVL = 51387282  # atricrypto3
SECONDS_IN_YEAR = 365 * 24 * 3600
INVESTED_AMOUNT = 1  # all returns are with respect to this initial investment amount - so best to keep in $1, simplest

# first, find the delta time of each pool (so we can get APY later):
ix1 = None
for ix1, yel in enumerate(data1["y"]):
    if abs(yel) > 0:
        break

seconds_ARB = (max(data1["xtime"]) - data1["xtime"][ix1]).total_seconds()

ix2 = None
for ix2, yel in enumerate(data2["y"]):
    if abs(yel) > 0:
        break
seconds_POL = (max(data2["xtime"]) - data2["xtime"][ix2]).total_seconds()

all_allocations_arb = []
all_apys = []
for percent_arb in np.linspace(0, 100, 100):

    percent_pol = 100 - percent_arb
    assert 0 <= percent_arb <= 100
    assert 0 <= percent_pol <= 100

    # we now invest $1, and the returns will all be on that dollar
    allocation_dollars_to_arb = INVESTED_AMOUNT * percent_arb / 100
    allocation_dollars_to_pol = INVESTED_AMOUNT * percent_pol / 100

    fraction_of_pool_arb = (
        allocation_dollars_to_arb / ARB_TVL
    )  # we then get the result in return per dollar
    fraction_of_pool_pol = allocation_dollars_to_pol / POL_TVL

    # ARB
    total_return_usd_arb = data1["y"].sum() * fraction_of_pool_arb
    # scale up to fill the year:
    factor = SECONDS_IN_YEAR / seconds_ARB
    annual_return_usd_arb = total_return_usd_arb * factor  # on the allocation into ARB

    # POL
    total_return_usd_pol = data2["y"].sum() * fraction_of_pool_pol
    # scale up to fill the year:
    factor = SECONDS_IN_YEAR / seconds_POL
    annual_return_usd_pol = total_return_usd_pol * factor

    total_annual_return_on_one_dollar = annual_return_usd_arb + annual_return_usd_pol
    the_apy = total_annual_return_on_one_dollar * 100

    all_allocations_arb.append(percent_arb)
    all_apys.append(the_apy)

plt.plot(all_allocations_arb, all_apys, "b-")
plt.grid()
plt.xlabel("% allocation to the ARB pool")
plt.ylabel("% APY")
plt.axvline(50, linestyle="--", color="k", alpha=0.8)
plt.savefig(os.path.join(store_here, "passive_investor.png"))

minapy = min(all_apys)
maxapy = max(all_apys)
print(f"min APY = {minapy:.1f}%")
print(f"max APY = {maxapy:.1f}%")
print(f"diff in APY = {maxapy - minapy:.1f} %-points")

# get the return of our static investor
STATIC_INVESTOR = 50  # percent allocation to ARB

theix = bisect.bisect_left(all_allocations_arb, STATIC_INVESTOR)
print(f"The APY of the static investor is: {all_apys[theix]:.1f}%")

# =========================================================================================
# ========================================================================================
#       COMPUTE THE MOST INTELLIGENT INVESTOR (CAN REACT INSTANTLY)
# ========================================================================================
# ========================================================================================

# TODO: the risk of the static investor is loosing out on 40% APY! But who knows how to allocate upfront?
# that's a value prop for us.

# TODO: we will lie somewhere in between static and fully dynamic (as computed below) and will be bound by
# TODO: time etc. The point we make is that we will gain more return than a static investor, even a lucky one
# TODO: (show that we beat the 80% too)

# just collect all the ARB revenues
# then collect all the POL revenues
# then do the math at the end
total_arb_rev = []
total_pol_rev = []
which_pool = []
revenue_collected_so_far = []  # keep track of portfolio value
for thistime in deltasxtime:

    # find the max return we could have gotten at this specific time step...
    arb_ix = bisect.bisect_left(data1["xtime"], thistime)
    arb_rev = data1["y"][arb_ix]

    pol_ix = bisect.bisect_left(data2["xtime"], thistime)
    pol_rev = data2["y"][pol_ix]

    # which is max? That's the one we will take
    maxix = np.argmax([arb_rev, pol_rev])
    if maxix == 0:
        total_arb_rev.append(arb_rev)
        total_pol_rev.append(0)

        therev = arb_rev
        which_pool.append("ARB")
    else:
        total_arb_rev.append(0)
        total_pol_rev.append(pol_rev)
        therev = pol_rev
        which_pool.append("POL")

    revenue_collected_so_far.append(therev)

assert len(total_arb_rev) == len(deltasxtime)
assert len(total_pol_rev) == len(deltasxtime)

# starting with $1, we now re-allocate based on our portfolio value
portfolio_value = INVESTED_AMOUNT  # start with $1

the_max_val = []
portfolio_value_list = [portfolio_value]
for rev, rev_arb, rev_pol, pool in zip(
    revenue_collected_so_far, total_arb_rev, total_pol_rev, which_pool
):

    # allocate what we have in our portfolio to the pool making the most this instant
    if pool == "ARB":
        fraction_of_pool_arb = (
            portfolio_value / ARB_TVL
        )  # we then get the result in return per dollar
        return_usd_arb = rev_arb * fraction_of_pool_arb  # on the allocation into ARB
        thereturn = return_usd_arb
        the_max_val.append(rev_arb)
    elif pool == "POL":
        fraction_of_pool_pol = (
            portfolio_value / POL_TVL
        )  # we then get the result in return per dollar
        return_usd_pol = rev_pol * fraction_of_pool_pol  # on the allocation into ARB
        thereturn = return_usd_pol
        the_max_val.append(rev_pol)
    else:
        raise Exception("wrong")

    # update portfolio val to what we earned:
    portfolio_value += thereturn
    portfolio_value_list.append(portfolio_value)

# now just take the portfolio value and compute annualized return
seconds = max([seconds_ARB, seconds_POL])
factor = SECONDS_IN_YEAR / seconds

total_return = portfolio_value * factor * 100

print(f"Total return for fully automated investor strategy = {total_return:.1f}%")

plt.figure()
x = np.arange(len(total_arb_rev))
plt.plot(x, total_arb_rev, 'g-', label="ARB")
plt.plot(x, total_pol_rev, 'r-', label="POL", alpha=0.8)
# plt.plot(x, the_max_val, 'b-', alpha=0.4, label="max")
plt.xlabel("time index")
plt.ylabel("pool fees")
plt.legend(loc="best")
plt.savefig(os.path.join(store_here, "fees.png"))


# ======================================================================
# ======================================================================
#       RUN THIS ALL VERSUS TIME
# ======================================================================
# ======================================================================

print("EXITING")
sys.exit(0)

plt.figure()
all_returns = []
all_percent_times_arb_better = []
slicedelta = 8000
ix = 0
sliceend = 0
while True:

    slicestart = slicedelta * ix
    sliceend = slicestart + slicedelta

    with open(FILE1, "rb") as fd:
        data1 = pickle.load(fd)

    with open(FILE2, "rb") as fd:
        data2 = pickle.load(fd)

    maxix = max(max(data1["x"]), max(data2["x"])) + 1

    datas = [max(data1["x"]), max(data2["x"])]
    maxaix = np.argmax(datas)

    deltasxtime = np.array([data1, data2])[maxaix]["xtime"]
    deltasx = list(range(maxix))
    deltasy = np.zeros(maxix)

    print(f"running {NAME1}...")
    for x, y in zip(data1["x"], data1["y"]):
        deltasy[x] += y

    print(f"running {NAME2}...")
    for x, y in zip(data2["x"], data2["y"]):
        deltasy[x] -= y

    firstix_not_zero = -1
    for x, y in zip(deltasx, deltasy):
        if abs(y) > 0:
            firstix_not_zero = x
            break

    # lastix_not_zero = -1
    # for x, y in zip(deltasx[::-1], deltasy[::-1]):
    #     if abs(y) > 0:
    #         lastix_not_zero = x
    #         break

    print("done")

    deltasx = deltasx[firstix_not_zero:]
    deltasy = deltasy[firstix_not_zero:]
    deltasxtime = deltasxtime[firstix_not_zero:]

    if sliceend >= len(deltasxtime):
        break

    # now take a chunk of this:
    deltasx = deltasx[slicestart:sliceend]
    deltasy = deltasy[slicestart:sliceend]
    deltasxtime = deltasxtime[slicestart:sliceend]

    assert len(deltasx) == slicedelta
    assert len(deltasy) == slicedelta
    assert len(deltasxtime) == slicedelta

    print(f"first date = {min(deltasxtime)}")
    print(f"last  date = {max(deltasxtime)}")

    # just collect all the ARB revenues
    # then collect all the POL revenues
    # then do the math at the end
    total_arb_rev = []
    total_pol_rev = []
    which_pool = []
    revenue_collected_so_far = []  # keep track of portfolio value
    for thistime in deltasxtime:

        # find the max return we could have gotten at this specific time step...
        arb_ix = bisect.bisect_left(data1["xtime"], thistime)
        arb_fee = data1["y"][arb_ix]

        pol_ix = bisect.bisect_left(data2["xtime"], thistime)
        pol_fee = data2["y"][pol_ix]

        arb_rev = arb_fee * (1 / ARB_TVL)  # scale to LP revenue
        pol_rev = pol_fee * (1 / POL_TVL)  # scale to LP revenue

        if arb_fee > 0:
            import pdb

            pdb.set_trace()

        if not (arb_fee > 0 or pol_fee > 0):
            which_pool.append("NONE")
            total_pol_rev.append(0)
            total_arb_rev.append(0)
            continue

        # which is max? That's the one we will take
        maxix = np.argmax([arb_rev, pol_rev])
        if maxix == 0:
            total_arb_rev.append(arb_fee)
            total_pol_rev.append(0)

            therev = arb_fee
            which_pool.append("ARB")
        else:
            total_arb_rev.append(0)
            total_pol_rev.append(pol_fee)
            therev = pol_fee
            which_pool.append("POL")

        revenue_collected_so_far.append(therev)

    # now find the %-age of times an ideal allocation is to ARB along the way:
    percent_times_arb_is_better = (
        np.sum(np.array(which_pool) == "ARB") / len(which_pool) * 100
    )

    all_percent_times_arb_better.append(percent_times_arb_is_better)

    assert len(total_arb_rev) == len(total_pol_rev) == len(deltasxtime)
    assert len(which_pool) == len(deltasxtime)

    # starting with $1, we now re-allocate based on our portfolio value
    portfolio_value = INVESTED_AMOUNT  # start with $1

    the_max_val = []
    portfolio_value_list = [portfolio_value]
    for rev, rev_arb, rev_pol, pool in zip(
        revenue_collected_so_far, total_arb_rev, total_pol_rev, which_pool
    ):

        # allocate what we have in our portfolio to the pool making the most this instant
        if pool == "ARB":
            fraction_of_pool_arb = (
                portfolio_value / ARB_TVL
            )  # we then get the result in return per dollar
            return_usd_arb = (
                rev_arb * fraction_of_pool_arb
            )  # on the allocation into ARB
            thereturn = return_usd_arb
            the_max_val.append(rev_arb)
        elif pool == "POL":
            fraction_of_pool_pol = (
                portfolio_value / POL_TVL
            )  # we then get the result in return per dollar
            return_usd_pol = (
                rev_pol * fraction_of_pool_pol
            )  # on the allocation into ARB
            thereturn = return_usd_pol
            the_max_val.append(rev_pol)
        else:
            continue

        # update portfolio val to what we earned:
        portfolio_value += thereturn
        portfolio_value_list.append(portfolio_value)

    # now just take the portfolio value and compute annualized return
    seconds = max([seconds_ARB, seconds_POL])
    factor = SECONDS_IN_YEAR / seconds

    total_return = portfolio_value * factor * 100

    all_returns.append(total_return)

    print(f"Total return for fully automated investor strategy = {total_return:.1f}%")
    sys.stdout.flush()

    # =================
    # NOW SIMULATE THE PASSIVE INVESTOR
    DAYS_IN_YEAR = 365
    INVESTED_AMOUNT = 1  # all returns are with respect to this initial investment amount - so best to keep in $1, simplest

    data1["xtime"] = data1["xtime"][firstix_not_zero:][slicestart:sliceend]
    data1["x"] = data1["x"][firstix_not_zero:][slicestart:sliceend]
    data1["y"] = data1["y"][firstix_not_zero:][slicestart:sliceend]

    data2["xtime"] = data2["xtime"][firstix_not_zero:][slicestart:sliceend]
    data2["x"] = data2["x"][firstix_not_zero:][slicestart:sliceend]
    data2["y"] = data2["y"][firstix_not_zero:][slicestart:sliceend]

    # first, find the delta time of each pool (so we can get APY later):

    time_in_ARB = (max(data1["xtime"]) - min(data1["xtime"])).total_seconds()
    time_in_POL = (max(data2["xtime"]) - min(data2["xtime"])).total_seconds()

    SECONDS_IN_YEAR = 365 * 24 * 3600

    all_allocations_arb = []
    all_apys = []
    for percent_arb in np.linspace(0, 100, 100):
        percent_pol = 100 - percent_arb
        assert 0 <= percent_arb <= 100
        assert 0 <= percent_pol <= 100

        # we now invest $1, and the returns will all be on that dollar
        allocation_dollars_to_arb = INVESTED_AMOUNT * percent_arb / 100
        allocation_dollars_to_pol = INVESTED_AMOUNT * percent_pol / 100

        fraction_of_pool_arb = (
            allocation_dollars_to_arb / ARB_TVL
        )  # we then get the result in return per dollar
        fraction_of_pool_pol = allocation_dollars_to_pol / POL_TVL

        # ARB
        total_return_usd = data1["y"].sum() * fraction_of_pool_arb
        # scale up to fill the year:
        factor = SECONDS_IN_YEAR / max([time_in_ARB, time_in_POL])
        annual_return_usd_arb = total_return_usd * factor  # on the allocation into ARB

        # POL
        total_return_usd = data2["y"].sum() * fraction_of_pool_pol
        # scale up to fill the year:
        factor = SECONDS_IN_YEAR / max([time_in_ARB, time_in_POL])
        annual_return_usd_pol = total_return_usd * factor

        total_annual_return_on_one_dollar = (
            annual_return_usd_arb + annual_return_usd_pol
        )
        the_apy = total_annual_return_on_one_dollar * 100

        all_allocations_arb.append(percent_arb)
        all_apys.append(the_apy)

    plt.plot(all_allocations_arb, all_apys, "b--", alpha=0.4)

    ix += 1

    plt.pause(0.05)


# plt.figure()
# plt.subplot(211)
# plt.plot(all_percent_times_arb_better, "bo-")
# plt.ylabel("% times ARB returns > POL returns")
# plt.subplot(212)
# plt.plot(all_returns)

import pdb

pdb.set_trace()
