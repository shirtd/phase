from phase.plot.mpl import PersistencePlot
from phase.plot.pyv import PYVPlot

from tqdm import tqdm
import numpy as np


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

class MetricData(Data):#, PYVPlot):
    module = 'input'
    args = []
    def __init__(self, data, name, title, prefix):
        features = ['Coord %d' % i for i in range(1,data.shape[-1]+1)]
        Data.__init__(self, data, name, title, prefix, features)

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
