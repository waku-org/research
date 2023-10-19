import matplotlib.pyplot as plt
import scienceplots
import numpy as np
import math
import random

def load(file):
    field = "arrival_diff="
    latencies = []
    with open(file, "r") as file:
        for line in file.readlines():
            if field in line:
                x = line.strip().split(field)[1].split(" ")[0]
                latencies.append(int(x))
    return np.array(latencies)

latencies = [load("latency_10kb.txt"), load("latency_100kb.txt"), load("latency_500kb.txt")]

with plt.style.context(['science', 'ieee']):
    fig, ax = plt.subplots()

    labels = []

    bp = ax.boxplot(latencies,notch=True, vert=True, patch_artist=True,
                    showfliers=True, whis=100000000000)

    for patch, color in zip(bp['boxes'], ['red', 'blue', 'green']):
        patch.set_facecolor(color)

    ax.set(title="Message rate (msg/s)", xlabel='Scenario', ylabel='Message propagation time (ms)')

    ax.grid(linestyle='-')
    my_legend = []
    for msg_size in [10, 100, 500]:
        my_legend.append("Message size: " + str(msg_size) + " kB")
    ax.legend([bp["boxes"][i] for i in range(len(my_legend))], my_legend, loc='upper left', fontsize=5)

    ax.autoscale(tight=False)

#means = [i.mean(axis=0) for i in q]
#stds =[i.std(axis=0) for i in q]
#per_95 = [np.percentile(i, 95) for i in q]
#for i, line in enumerate(bp['medians']):
#    x, y = line.get_xydata()[1]
#    text = r' $ \mu =$ ' + '{:.2f}\n'.format(means[i]) + r' $ p_{95} = $ ' + '{:.2f}'.format(per_95[i])
#    ax.annotate(text, xy=(x+0.1, y), fontsize=6)
#
#

for i, line in enumerate(bp['medians']):
    x, y = line.get_xydata()[1]
    text = r' $ \mu =$ ' + '{:.0f} ms\n'.format(latencies[i].mean(axis=0)) + r' $ p_{95} = $ ' + '{:.0f} ms'.format(np.percentile(latencies[i], 95))
    ax.annotate(text, xy=(x + 0.1, y), fontsize=6)

fig.savefig('plot.jpg', dpi=600)