from phase.topology.util import get_lim

import matplotlib.pyplot as plt
import numpy as np
import os


def init_diagram(axis, lim):
    axis.plot([0, 1.2*lim], [0,1.2*lim], c='black', alpha=0.5, zorder=1)
    axis.plot([0, lim], [lim,lim], c='black', ls=':', alpha=0.5, zorder=1)
    axis.plot([lim, lim], [lim, 1.2*lim], c='black', ls=':', alpha=0.5, zorder=1)

def lim_dgm(dgm, lim):
    return np.array([[b, d if d < np.inf else 1.2*lim] for b,d in dgm])

def plot_diagrams(axis, dgms, lim=None, init=True):
    if lim is None:
        lim = get_lim(dgms)
    if init:
        init_diagram(axis, lim)
    elems = []
    for dim, dgm in enumerate(dgms):
        if len(dgm):
            d = lim_dgm(dgm, lim)
            elems += [axis.scatter(d[:,0], d[:,1], s=7, zorder=2, alpha=0.3, label='H%d' % dim)]
        else:
            elems += [axis.scatter([], [], s=7, zorder=2, alpha=0.3, label='H%d' % dim)]
    if init:
        axis.legend()
    return lim, elems

def save_plot(dir, prefix, name, dpi=500):
    fname = os.path.join(dir,'%s_%s.png' % (prefix, name))
    print('saving %s' % fname)
    plt.savefig(fname, dpi=dpi)

def plot_histo(axis, L, histo, name='', ymax=None, stat='count'):
    if ymax is not None:
        ax.set_ylim(0, ymax)
    for dim, h in enumerate(histo):
        axis.plot(L[1:] - 1 / len(L), h, label='H%d' % dim)
    fig.suptitle('TPers histogram %s' % name)
    ax.set_xlabel('TPers')
    ax.set_ylabel(stat)
    ax.legend()
    plt.tight_layout()
