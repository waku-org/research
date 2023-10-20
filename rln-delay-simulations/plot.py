import matplotlib.pyplot as plt
import scienceplots
import numpy as np
from analyze import load

latencies = [load("raw/latency_10kb.txt", "arrival_diff="),
             load("raw/latency_100kb.txt", "arrival_diff="),
             load("raw/latency_500kb.txt", "arrival_diff=")]

print(latencies)

with plt.style.context(['science', 'ieee']):
    fig, ax = plt.subplots()
    bp = ax.boxplot(latencies,notch=True, vert=True, patch_artist=True,
                    showfliers=True, whis=100000000000)

    for patch, color in zip(bp['boxes'], ['red', 'blue', 'green']):
        patch.set_facecolor(color)

    ax.set(title="Message latencies distribution\nD=6 nodes=1000 samples="+str(latencies[1].size), xlabel='Scenario', ylabel='Message propagation time (ms)')
    ax.grid(linestyle='-')
    my_legend = []
    for msg_size in [10, 100, 500]:
        my_legend.append("Message size: " + str(msg_size) + " kB")
    ax.legend([bp["boxes"][i] for i in range(len(my_legend))], my_legend, loc='upper left', fontsize=5)

for i, line in enumerate(bp['medians']):
    x, y = line.get_xydata()[1]
    text = r' $ \mu =$ ' + '{:.0f} ms\n'.format(latencies[i].mean(axis=0)) + r' $ p_{95} = $ ' + '{:.0f} ms'.format(np.percentile(latencies[i], 95))
    ax.annotate(text, xy=(x + 0.1, y), fontsize=6)

fig.set_size_inches(4, 3)
fig.savefig('plot.jpg', dpi=600)