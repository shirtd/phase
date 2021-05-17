from phase.data import BOUNDS, parse_file
from phase.util import format_float

from phase.plot.mpl import PersistencePlot
from phase.plot.pyv import PYVPlot

from tqdm import tqdm
import numpy as np
import os


class Data:
    module = 'input'
    args = []
    def __init__(self, data, name, title, prefix, features):
        self.data, self.features = data, features
        self.name, self.title, self.prefix = name, title, prefix
    def __iter__(self):
        yield from self.data
    def __repr__(self):
        return self.title
    def __getitem__(self, i):
        return self.data[i]
    def __len__(self):
        return len(self.data)

class MetricData(Data):
    module = 'input'
    args = []
    def __init__(self, data, name, title, prefix):
        features = ['Coord %d' % i for i in range(1,data.shape[-1]+1)]
        Data.__init__(self, data, name, title, prefix, features)


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

class PersistenceData(Data, PersistencePlot):
    module = 'persist'
    args = []
    def __init__(self, input_data, data, name, title, prefix, dim):
        self.dim, self.input_data = dim, input_data
        features = ['H%d' % d for d in range(dim+1)]
        Data.__init__(self, data, name, title, prefix, features)
        PersistencePlot.__init__(self)
    def __call__(self, d, *args, **kwargs):
        pass
    def run(self, input_data, prefix, *args, **kwargs):
        return [self(d, *args, **kwargs) for d in tqdm(input_data, total=len(input_data), desc='[ %s persistence' % prefix)]

class MyPersistence(PersistenceData):
    args = ['dim', 'delta', 'omega', 'coh']
    @classmethod
    def get_name(cls, input_data, delta, omega, coh,  *args, **kwargs):
        name = '%s_%s' % (input_data.name, cls.get_prefix())
        if delta > 0 or omega > 0:
            d = {'delta' : delta, 'omega' : omega}
            s = ['%s%s' % (l,format_float(v)) for l,v in d.items() if v > 0]
            name = '-'.join([name] + s)
        if coh:
            name += '-coh'
        return name
    @classmethod
    def get_title(cls, input_data, delta, omega, coh, *args, **kwargs):
        title = '%s %s' % (input_data.title, cls.get_prefix())
        if delta > 0 or omega > 0:
            d = {'delta' : delta, 'omega' : omega}
            s = ['%s=%g' % (l,v) for l,v in d.items() if v > 0]
            title = '%s (%s)' % (title, ','.join(s))
        if coh:
            title += '-coh'
        return title
    def __init__(self, input_data, dim, delta, omega, coh):
        name = self.get_name(input_data, delta, omega, coh)
        title = self.get_title(input_data, delta, omega, coh)
        prefix = self.get_prefix(delta, omega, coh)
        self.delta, self.omega, self.coh = delta, omega, coh
        self.bounds = (BOUNDS[0]+delta, BOUNDS[1]-delta)
        self.chain_data = self.run(input_data, prefix, input_data.data.shape[-1])
        data = [d.get_diagram() for d in self.chain_data]
        PersistenceData.__init__(self, input_data, data, name, title, prefix, dim)
    def is_boundary(self, p):
        return not all(self.bounds[0] < c < self.bounds[1] for c in p)
    def get_boundary(self, P, F):
        if self.delta > 0 or self.omega > 0:
            Q = {i for i,p in enumerate(P) if self.is_boundary(p)}
            return {i for i,s in enumerate(F) if all(v in Q for v in s) or s.data['alpha'] < self.omega}
        return set()
