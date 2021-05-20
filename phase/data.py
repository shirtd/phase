import pickle as pkl
import numpy as np
import sys, os


DIR = os.path.join('data')
DATA = {'lennard-jones' : ['melt.xyz'],
        'water-first-order' : ['ih_hda.xyz', 'lda_hda.xyz'],
        'water-glass' : ['traj.xyz']}
DATASET = 'lennard-jones'
LOGFILE = 'melt.xyz'


def parse_line(line):
    l = line.replace('\n', '').split()
    return {'atom' : l[0], 'coord' : list(map(float, l[1:]))}

def parse_file(fname, frng=None):
    frng = (0, np.inf) if frng is None else frng
    frame, frames = 0, []
    with open(fname, 'r') as f:
        try:
            while f and frame < frng[1]:
                n = int(next(f))
                bounds = next(f).replace('\n', '').split()
                if not frng[0] <= frame < frng[1]:
                    for i in range(n):
                        next(f)
                else:
                    dat = [parse_line(next(f)) for i in range(n)]
                    frames.append({'bounds' : bounds,
                                    'atoms' : [d['atom'] for d in dat],
                                    'points' : [d['coord'] for d in dat]})
                frame += 1
        except StopIteration:
            pass
    return frames

def get_bounds(input_data, dataset):
    if dataset == 'lennard-jones':
        return np.array([[8., 8., 8.] for _ in input_data])
    return np.array([[float(c) for c in d['bounds']] for d in input_data])
