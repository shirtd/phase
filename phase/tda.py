from phase.base import PersistenceData, MyPersistenceBase, MyPersistence#, BOUNDS
from phase.util import format_float

from phase.topology.cells import DualComplex
from phase.topology.simplicial import AlphaComplex
from phase.topology.chains import BoundaryMatrix, Filtration
from phase.topology.persist import DiagramBase, Diagram

from phase.plot.pyv import PYVPlot, ChainPlot

from ripser import ripser
import numpy.linalg as la
import numpy as np


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

class AlphaPersistenceBase(MyPersistenceBase):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'base-alpha'
    def __call__(self, P, dim):
        P.dtype = float
        K = AlphaComplex(P, 'alpha')
        F = BoundaryMatrix(K.get_sequence('alpha'),dim)#, dim), dim)
        R = self.get_boundary(P, F)
        dgm = DiagramBase(F.get_range(R), self.coh)
        dgm._clearing_reduce(F, R)
        return dgm.get_diagram(F, 'alpha', False)

class VoronoiPersistenceBase(MyPersistenceBase):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'base-dual'
    def __call__(self, P, dim):
        P.dtype = float
        K = AlphaComplex(P, 'alpha')
        L = DualComplex(K, 'alpha')
        F = BoundaryMatrix(K.get_sequence('alpha'), dim)#, P.shape[-1]), P.shape[-1])
        G = BoundaryMatrix(L.get_sequence('alpha', True), dim)#, dim, True), dim)
        R = self.get_boundary(P, F)
        S = {G.index(L(F[i])) for i in R}# if L(F[i]).dim <= dim}
        dgm = DiagramBase(G.get_range(S), self.coh)
        dgm._clearing_reduce(G, S)
        return dgm.get_diagram(G, 'alpha', True)

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
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'dual'
    def __call__(self, P, dim):
        P.dtype = float
        K = AlphaComplex(P, 'alpha')
        F = Filtration(K, 'alpha')
        L = DualComplex(K, 'alpha')
        G = Filtration(L, 'alpha', True)
        R = self.get_boundary(P, F)
        S = {G.index(L(F[i])) for i in R}# if L(F[i]).dim <= dim}
        return Diagram(G, S, self.coh)
