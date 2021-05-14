from phase.base import PersistenceData
from phase.data import BOUNDS
from phase.simplicial import DioComplex, Filtration
from phase.persist import phcol
from phase.plot.pyv import PYVPlot, ChainPlot
from phase.plot.mpl import PersistencePlot
from phase.plot.interact import Interact

from ripser import ripser
import numpy.linalg as la
import dionysus as dio
import numpy as np
import diode


class RipsPersistence(PersistenceData):
    args = ['dim', 'thresh']
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'Rips'
    @classmethod
    def get_name(cls, input_data, *args, **kwargs):
        return '%s_rips' % input_data.name
    @classmethod
    def get_title(cls, input_data, *args, **kwargs):
        return '%s rips' % input_data.title
    def __init__(self, input_data, dim, thresh):
        name = self.get_name(input_data)
        title = self.get_title(input_data)
        prefix = self.get_prefix()
        data = self.run(input_data, prefix, dim, thresh)
        PersistenceData.__init__(self, input_data, data, name, title, prefix, dim)
    def __call__(self, d, dim, thresh):
        return ripser(d, dim, thresh)['dgms']

def format_float(f):
    if f.is_integer():
        return int(f)
    e = 0
    while not f.is_integer():
        f *= 10
        e -= 1
    return '%de%d' % (int(f), e)

class AlphaPersistence(PersistenceData):
    args = ['dim', 'delta', 'omega']
    @classmethod
    def get_prefix(cls, delta, omega, *args, **kwargs):
        return 'Alpha'
    @classmethod
    def get_name(cls, input_data, delta, omega,  *args, **kwargs):
        name = '%s_alpha' % input_data.name
        if delta > 0 or omega > 0:
            d = {'delta' : delta, 'omega' : omega}
            s = ['%s%s' % (l,format_float(v)) for l,v in d.items() if v > 0]
            name = '-'.join([name] + s)
        return name
    @classmethod
    def get_title(cls, input_data, delta, omega, *args, **kwargs):
        title = '%s alpha' % input_data.title
        if delta > 0 or omega > 0:
            d = {'delta' : delta, 'omega' : omega}
            s = ['%s=%g' % (l,v) for l,v in d.items() if v > 0]
            title = '%s (%s)' % (title, ','.join(s))
        return title
    def __init__(self, input_data, dim, delta, omega):
        name = self.get_name(input_data, delta, omega)
        title = self.get_title(input_data, delta, omega)
        prefix = self.get_prefix(delta, omega)
        self.delta, self.omega = delta, omega
        self.bounds = (BOUNDS[0]+delta, BOUNDS[1]-delta)
        dim = input_data.data.shape[-1]
        self.chain_data = self.run(input_data, prefix, dim)
        data = [d.get_diagram() for d in self.chain_data]
        PersistenceData.__init__(self, input_data, data, name, title, prefix, dim)
        self.current_dgm = None
    def is_boundary(self, p):
        return not all(self.bounds[0] < c < self.bounds[1] for c in p)
    def get_boundary(self, P, F):
        if self.delta > 0 or self.omega > 0:
            Q = {i for i,p in enumerate(P) if self.is_boundary(p)}
            return {i for i,s in enumerate(F) if all(v in Q for v in s) or s.data['alpha'] < self.omega}
        return set()
    def __call__(self, P, dim):
        P.dtype = float
        Fdio = dio.Filtration(diode.fill_alpha_shapes(P))
        K = DioComplex(Fdio, 'alpha', dim)
        F = Filtration(K, 'alpha')
        R = self.get_boundary(P, F)
        return phcol(F, R)
    def plot(self, frame, *args, **kwargs):
        res = PersistenceData.plot(self, frame, *args, **kwargs)
        self.current_dgm = self.chain_data[frame]
        return res
