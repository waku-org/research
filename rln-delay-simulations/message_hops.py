from math import ceil
from numpy import log
from numpy import ceil
import matplotlib.pyplot as plt
import numpy as np
import scienceplots

L = 1      # latency in ms (msg prop + rln proof verif, etc)
N1 = 1000    # number of nodes in the network (1)
N2 = 10000   # number of nodes in the network (2)
N3 = 100000  # number of nodes in the network (3)

def delay_last_hop(n, d, l):
    # multiply by l for latencies
    return ceil(log(n)/log(d))

ds = np.arange(2,15)
ls = np.ones(len(ds))*L

# astype(int) is ok since ceil() returns integers
delays_1 = delay_last_hop(np.ones(len(ds))*N1, ds, ls).astype(int)
delays_2 = delay_last_hop(np.ones(len(ds))*N2, ds, ls).astype(int)
delays_3 = delay_last_hop(np.ones(len(ds))*N3, ds, ls).astype(int)

with plt.style.context(['science', 'ieee']):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(ds, delays_1, color='r', label=str(N1)+" nodes")
    ax1.plot(ds, delays_2, color='g', label=str(N2)+" nodes")
    ax1.plot(ds, delays_3, color='b', label=str(N3)+" nodes")
    ax2.plot(ds, ds, color='y', label="Bandwidth\namplification")
    ax1.autoscale(tight=True)
    ax2.autoscale(tight=True)
    ax1.legend(loc=(0.08, 0.7))
    ax2.legend(loc=(0.5, 0.76))
    ax1.set(title='$h_{max}$ and bandwidth amplification depending on node degree $D$\n')
    ax1.set(**dict(xlabel='Node degree (D)', ylabel='Maximum number of hops ($h_{max}$)\n'))
    ax2.set(**dict(ylabel='\nBandwidth amplification'))

    # Set the limits of the x-axis and y-axis
    ax1.set_xlim(2, 15)
    ax1.set_ylim(2, ax1.get_ylim()[1])  # Ensure that the lower limit is 2
    
    # Set the limits of the second y-axis to match the first y-axis
    ax2.set_ylim(ax1.get_ylim())

    fig.savefig('message_hops.svg', dpi=600)
    plt.close()

