from phase.base import PersistenceData, MyPersistence, BOUNDS
from phase.util import format_float

from phase.topology.cells import DualComplex
from phase.topology.simplicial import AlphaComplex
from phase.topology.chains import Filtration
from phase.topology.persist import Diagram

from phase.plot.pyv import PYVPlot, ChainPlot
from phase.plot.mpl import PersistencePlot
from phase.plot.interact import Interact

from phase.duality import VoronoiDual

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


class AlphaPersistence(MyPersistence):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'alpha'
    def __call__(self, P, dim):
        P.dtype = float
        K = AlphaComplex(P, 'alpha')
        F = Filtration(K, 'alpha')
        R = self.get_boundary(P, F)
        return Diagram(F, R, self.coh)

class VoronoiPersistence(MyPersistence):
    args = ['dim', 'delta', 'omega', 'coh']
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'dual'
    def __call__(self, P, dim):
        P.dtype = float
        K = AlphaComplex(P, 'alpha')
        F = Filtration(K, 'alpha')
        L = DualComplex(K, 'alpha')
        for i,p in enumerate(L.P):
            for j,c in enumerate(p):
                if c < BOUNDS[0]:
                    L.P[i,j] = BOUNDS[0] # - (BOUNDS[1] - BOUNDS[0]) / 4
                elif c > BOUNDS[1]:
                    L.P[i,j] = BOUNDS[1] # * (1 + 1/4)
        G = Filtration(L, 'alpha', True)
        R = self.get_boundary(P, F)
        S = {G.index(L(F[i])) for i in R}
        return Diagram(G, S, self.coh)
