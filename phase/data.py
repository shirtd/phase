from phase.base import *

import pickle as pkl
import numpy as np
import sys, os
import click

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

class InputData(MetricData):
    args = ['directory', 'dataset', 'file', 'frames']
    @classmethod
    def get_prefix(cls, directory, dataset, file, frames):
        return os.path.splitext(file)[0]
    @classmethod
    def get_name(cls, directory, dataset, file, frames):
        prefix = cls.get_prefix(directory, dataset, file, frames)
        name = '%s-%s' % (dataset, prefix)
        if frames is not None:
            return '%s_%d-%d' % (name, frames[0], frames[1])
        return name
    @classmethod
    def get_title(cls, directory, dataset, file, frames):
        prefix = cls.get_prefix(directory, dataset, file, frames)
        title = '%s, %s' % (dataset, prefix)
        if frames is not None:
            return '%s frames %d-%d' % (title, frames[0], frames[1])
        return title
    def __init__(self, directory, dataset, file, frames):
        self.directory, self.dataset, self.file = directory, dataset, file
        self.path = os.path.join(directory, dataset, file)
        print('[ Loading %s' % self.path)
        input_data = parse_file(self.path)
        prefix = self.get_prefix(directory, dataset, file, frames)
        name = self.get_name(directory, dataset, file, frames)
        title = self.get_title(directory, dataset, file, frames)
        frames = frames if frames is not None else (0, len(input_data))
        data = np.stack([np.array(d['points']) for d in input_data[frames[0]:frames[1]]])
        MetricData.__init__(self, data, name, title, prefix)
