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

# Best (1 hop) and worst (4 hops) latencies in ms
# See Table 2 from paper
multi_host_simulations = {
    "2kb": [364, 709],
    "25kb": [436, 1084],
    "100kb": [471, 1922],
    "500kb": [564, 2988]
}

with plt.style.context(['science', 'ieee']):
    fig, ax = plt.subplots(2, 2)
    possitions = [
        ("2kb", ax[0][0]),
        ("25kb", ax[0][1]),
        ("100kb", ax[1][0]),
        ("500kb", ax[1][1])
    ]

    for (size, pos) in possitions:
        # Plot single host results
        latencies.hist(size, bins=num_bins, ax=pos, density=True)

        # Plot multi host results
        pos.axvline(x=multi_host_simulations[size][0], color='red', linestyle='--')
        pos.axvline(x=multi_host_simulations[size][1], color='red', linestyle='--')

        pos.grid(False)
        title = ('size={size}\n' + r'$\mu$={mean:.0f} $p_{{95}}$={p95:.0f} min={min:.0f} max={max:.0f}').format(
            size=size,
            mean=latencies[size].mean(axis=0),
            p95=np.percentile(latencies[size], 95),
            min=latencies[size].min(),
            max=latencies[size].max())
        pos.set_title(title, fontsize=8)

    ax[0][0].set(ylabel='Cumulative message share')
    ax[1][0].set(xlabel='Latency (ms)', ylabel='Cumulative message share')
    ax[1][1].set(xlabel='Latency (ms)')

plt.tight_layout(pad=0, w_pad=0, h_pad=0.7)
fig.set_size_inches(4, 3)
fig.savefig('paper_distribution.svg', dpi=600)