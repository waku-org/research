import matplotlib.pyplot as plt
import scienceplots
import numpy as np
import pandas as pd
from analyze import load

latencies = pd.DataFrame({
    "2kb": load("raw/paper_latency_2kb_v2.txt", "arrival_diff="),
    "25kb": load("raw/paper_latency_25kb_v2.txt", "arrival_diff="),
    "100kb": load("raw/paper_latency_100kb_v2.txt", "arrival_diff="),
    "500kb": load("raw/paper_latency_500kb_v2.txt", "arrival_diff=")})

num_bins = 50
#fig, ax = plt.subplots(2, 2)





with plt.style.context(['science', 'ieee']):
    fig, ax = plt.subplots(2, 2)
    possitions = [
        ("2kb", ax[0][0]),
        ("25kb", ax[0][1]),
        ("100kb", ax[1][0]),
        ("500kb", ax[1][1])
    ]

    for (size, pos) in possitions:
        latencies.hist(size, bins=num_bins, ax=pos)
        pos.grid(False)
        text = r'$ \mu=$' + '{:.0f};'.format(latencies[size].mean(axis=0)) + r' $ p_{95}=$' + '{:.0f};'.format(
            np.percentile(latencies[size], 95)) + ' max={:.0f}'.format(latencies[size].max())
        pos.set_title(f"msgsize={size}; " + text, fontsize=6)

    ax[0][0].set(ylabel='Amount samples')
    ax[1][0].set(xlabel='Latency (ms)', ylabel='Amount samples')
    ax[1][1].set(xlabel='Latency (ms)')

fig.set_size_inches(4, 3)
fig.savefig('paper_distribution.svg', dpi=600)