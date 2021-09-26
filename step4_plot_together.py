# -*- coding: utf-8 -*-
"""

@ author Jesper Kristensen | Composable Finance
All Rights Reserved
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==================
FILE1 = "data/arb_vis_2021-09-24_22_57_19.pkl"
FILE2 = "data/pol_vis_2021-09-24_23_23_50.pkl"
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

lastix_not_zero = -1
for x, y in zip(deltasx[::-1], deltasy[::-1]):
    if abs(y) > 0:
        lastix_not_zero = x
        break

print("done")

deltasx = deltasx[firstix_not_zero:lastix_not_zero]
deltasy = deltasy[firstix_not_zero:lastix_not_zero]
deltasxtime = deltasxtime[firstix_not_zero:lastix_not_zero]

plt.scatter(deltasxtime, deltasy / 1000, color="r", marker=".")
plt.xlabel("time")
plt.ylabel(f"exchange volume (in 1000s USD); positive: {NAME1} > {NAME2}")
plt.grid()

plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("volume_usd_delta.png", dpi=800, format="png")
