import pickle as pkl
import numpy as np
import sys, os


DIR = os.path.join('data')
DATA = {'lennard-jones' : ['melt.xyz'], # , 'thermo.dat'],
        'water-first-order' : ['ih_hda.xyz', 'lda_hda.xyz'],
        'water-glass' : ['traj.xyz']}
DATASET = 'lennard-jones' # 'water-first-order' # 'water-glass' #
LOGFILE = 'melt.xyz' # 'ih_hda.xyz' # 'traj.xyz' #
BOUNDS = (0, 8)


def parse_line(line):
    l = line.replace('\n', '').split()
    return {'atom' : l[0], 'coord' : list(map(float, l[1:]))}


def parse_file(fname):
    with open(fname, 'r') as f:
        frames = []
        try:
            while f:
                n = int(next(f))
                # centroid = np.array(list(map(float, next(f).replace('\n', '').split())))
                centroid = np.array([0,0,0])
                next(f)
                dat = [parse_line(next(f)) for i in range(n)]
                frames.append({'centroid' : centroid,
                                'atoms' : [d['atom'] for d in dat],
                                'points' : [d['coord'] for d in dat]})
        except StopIteration:
            pass
    return frames
