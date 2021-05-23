from phase.base import Data

from phase.plot.mpl import TimeSeriesPlot, plt

from tqdm import tqdm
import numpy as np


class TPers(Data, TimeSeriesPlot):
    module = 'analyze'
    args = ['dim', 'pmin', 'pmax',
            'bmin', 'bmax', 'dmin', 'dmax',
            'average', 'count', 'lim', 'verbose']
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'TPers'
    @classmethod
    def get_name(cls, input_data, *args, **kwargs):
        return '%s_tpers' % input_data.name
    @classmethod
    def get_title(cls, input_data, *args, **kwargs):
        return '%s TPers' % input_data.title
    def __init__(self, input_data, dim, pmin, pmax, bmin, bmax, dmin, dmax, average, count, lim, verbose):
        features =  ['H%d' % d for d in range(dim)]
        self.dim, self.lim = dim, lim * input_data.limits.max()
        self.prng, self.brng, self.drng = (pmin, pmax), (bmin,bmax), (dmin,dmax)
        it = tqdm(input_data, total=len(input_data), desc='[ tpers') if verbose else input_data
        data = np.vstack([self(dgms, dim, average, count) for dgms in it])
        Data.__init__(self, data, input_data.bounds, input_data)
        TimeSeriesPlot.__init__(self, features, dim+1, 1, sharex=True, figsize=(12,8))
    def inrng(self, p):
        return (self.prng[0] <= p[1] - p[0] < self.prng[1]
            and self.brng[0] <= p[0] < self.brng[1]
            and self.drng[0] <= p[1] < self.drng[1])
    def get_range(self, dgm):
        return dgm[[i for i,p in enumerate(dgm) if self.inrng(p)]]
    def __call__(self, dgms, dim, average, count):
        ps = [[d - b for b,d in self.get_range(dgm)] for dgm in dgms[:dim+1]]
        return ([sum(p) / len(p) if len(p) else 0 for p in ps] if average
            else [len(p) for p in ps] if count
            else [sum(p) for p in ps])
