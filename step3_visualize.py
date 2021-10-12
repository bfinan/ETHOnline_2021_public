# -*- coding: utf-8 -*-
"""

@author Jesper Kristensen | Composable Finance.
All Rights Reserved.
"""

import bisect
import datetime
from datetime import timedelta
import glob
import os
import pickle
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import seaborn as sns

# sns.set_theme(style="whitegrid", palette="pastel")
sns.set_theme()

DATAPATH = "data"

# ======================
# FILE = "arb_post_2021-09-24_22_57_19.pkl"
# FILE = "pol_post_2021-09-24_23_23_50.pkl"

FILE = "arb_post_2021-09-26_23_30_15.pkl"
# FILE = "pol_post_2021-09-26_23_10_09.pkl"
# ======================

FILE = os.path.join(DATAPATH, FILE)

FILENAME_OUT = FILE.split("/")[1].split("_")[0]
assert os.path.isfile(FILE), "File not found!"

# files = sorted(glob.glob(os.path.join(DATAPATH, "*_post_*.pkl")))
# latest = files[-1]

timestamp = FILE.split("post_")[1].split(".")[0]

print(FILE)

with open(FILE, "rb") as fd:
    df = pickle.load(fd)

# df = df.rolling(10).median()
# df.dropna(inplace=True)

# Create time grid
def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta


MINDATETIME = datetime.datetime(2021, 1, 1)
MAXDATETIME = datetime.datetime.strptime(
    timestamp, "%Y-%m-%d_%H_%M_%S"
) + datetime.timedelta(seconds=60)

MINDATE = MINDATETIME.date()
MAXDATE = MAXDATETIME.date() + datetime.timedelta(days=1)
assert (
    datetime.datetime.strptime(min(df.index), "%m-%d-%YT%H:%M:%S").date() >= MINDATE
) and (datetime.datetime.strptime(min(df.index), "%m-%d-%YT%H:%M:%S").date() < MAXDATE)

timegrid = [
    dt for dt in datetime_range(MINDATETIME, MAXDATETIME, timedelta(seconds=10))
]

# now snap the (data) x values on to the grid
x = [datetime.datetime.strptime(xx, "%m-%d-%YT%H:%M:%S") for xx in df.index]

df["time"] = x
df["range"] = range(len(df))

y = df[FILENAME_OUT.upper() + "_LP_REV"].values

timegrid_ix = list(range(len(timegrid) + 1))
values = np.zeros(len(timegrid) + 1)
for xel, yel in zip(x, y):
    pos = bisect.bisect_left(timegrid, xel)
    if xel.second < 15:
        pos -= 1
    pos = max(pos, 0)
    values[pos] = yel

xtimedense = timegrid
xdense = timegrid_ix
ydense = values

# find smallest delta
# smallest_diff = min(np.diff(x))

# FEEFRAC = 0.135 * 0.5 / 100  # fee in fraction to LPs
# lp_revenue = y * FEEFRAC

# from scipy.interpolate import interp1d
# f2 = interp1d(x, y, kind='cubic')

# sns.regplot(x="range", y="ARB", data=df, color='g')
plt.scatter(x, y, color="g", marker=".")
# plt.plot(x, f2)

# plt.figure()
# plt.subplot(211)
# plt.plot(x, y, "k-", alpha=0.6)
# plt.ylabel("USD volume ($)")
#
# plt.subplot(212)
# plt.plot(x, lp_revenue, "g--")
# plt.ylabel("LP revenue ($)")
#
# plt.grid()
# plt.xlabel("time")
#
# daystart = "2021-09-14"
# dayend = "2021-09-15"
# dfday = df[(np.array(x) > datetime.datetime.strptime(daystart, "%Y-%m-%d")) & (np.array(x) < datetime.datetime.strptime(dayend, "%Y-%m-%d"))]
# thesum = dfday.sum().iloc[0]

data = {"xtime": xtimedense, "x": xdense, "y": ydense}

with open(os.path.join(DATAPATH, f"{FILENAME_OUT}_vis_{timestamp}.pkl"), "wb") as fd:
    pickle.dump(data, fd)

plt.show()
