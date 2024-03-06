import matplotlib.pyplot as plt
import scienceplots
import numpy as np
import pandas as pd
from analyze import load

latencies = pd.DataFrame({
    "2 KB": load("raw/paper_latency_2kb_v2.txt", "arrival_diff="),
    "25 KB": load("raw/paper_latency_25kb_v2.txt", "arrival_diff="),
    "100 KB": load("raw/paper_latency_100kb_v2.txt", "arrival_diff="),
    "500 KB": load("raw/paper_latency_500kb_v2.txt", "arrival_diff=")})

num_bins = 50

# Best (1 hop) and worst (4 hops) latencies in ms
# See Table 2 from paper
multi_host_simulations = {
    # msg_size: min/max
    "2 KB": [280, 498],
    "25 KB": [349, 931],
    "100 KB": [350, 1781],
    "500 KB": [539, 3141],
}

with plt.style.context(['science', 'ieee']):
    fig, ax = plt.subplots(2, 2)
    possitions = [
        ("2 KB", ax[0][0]),
        ("25 KB", ax[0][1]),
        ("100 KB", ax[1][0]),
        ("500 KB", ax[1][1])
    ]

    for (size, pos) in possitions:
        # Plot single host results
        latencies.hist(size, bins=num_bins, ax=pos, density=True, label="Single-host")

        # Plot multi host results
        pos.axvline(x=multi_host_simulations[size][0], color='red', linestyle='--', label="Multi-host")
        pos.axvline(x=multi_host_simulations[size][1], color='red', linestyle='--')

        pos.grid(False)
        title = ('Message Size = {size}'.format(size=size))
        pos.set_title(title, fontsize=8)
        if size == "25kb":
            pos.legend(fontsize="5", loc="upper left")
        else:
            pos.legend(fontsize="5", loc="best")

    ax[0][0].set(ylabel='Message share')
    ax[1][0].set(xlabel='Latency (ms)', ylabel='Message share')
    ax[1][1].set(xlabel='Latency (ms)')

plt.tight_layout(pad=0, w_pad=0, h_pad=0.7)
fig.set_size_inches(4, 3)
fig.savefig('paper_distribution.svg', dpi=600)