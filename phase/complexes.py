from phase.topology.cells import DualComplex
from phase.topology.simplicial import AlphaComplex
from phase.base import DataTransformation

from phase.topology.chains import BoundaryMatrix, Filtration
from phase.topology.persist import DiagramBase, Diagram

import numpy.linalg as la
import numpy as np


class ComplexData(DataTransformation):
    module = 'complex'
    args = ['dim'] + DataTransformation.args
    @classmethod
    def get_name(cls, input_data, dim, *args, **kwargs):
        dstr = '' if dim == input_data.shape[-1] else '%dD' % dim
        return '%s_%s%s' % (input_data.name, cls.get_prefix(), dstr)
    @classmethod
    def get_title(cls, input_data, dim, *args, **kwargs):
        dstr = '' if dim == input_data.shape[-1] else '%dD' % dim
        return '%s %s %s' % (input_data.title, cls.get_prefix(), dstr)
    def __init__(self, input_data, dim, parallel, verbose, *args, **kwargs):
        self.dim, self.input_dim = dim, input_data.dim
        DataTransformation.__init__(self, input_data, parallel, verbose, dim, *args, **kwargs)
    def is_boundary(self, p, d):
        return not all(d < c < u - d for c,u in zip(p, self.limits))
    def get_boundary(self, P, F, d):
        if d > 0:
            Q = {i for i,p in enumerate(P) if self.is_boundary(p, d)}
            return {i for i,s in enumerate(F) if all(v in Q for v in s)}
        return set()
    def get_filtration(self, K, d, cycle_reps=True):
        F = (Filtration if cycle_reps else BoundaryMatrix)(K, 'alpha', False)
        return F, self.get_boundary(K.P, F, d)

class AlphaComplexData(ComplexData):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'alpha'
    def __call__(self, d, verbose):
        return AlphaComplex(d, 'alpha', self.dim, verbose)

class VoronoiComplexData(ComplexData):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'dual'
    def __call__(self, d, verbose):
        K = AlphaComplex(d, 'alpha', self.input_dim, verbose)
        return DualComplex(K, 'alpha', self.dim, verbose)
    def get_filtration(self, L, d, cycle_reps=True):
        F, R = ComplexData.get_filtration(self, L.K, d, cycle_reps)
        G = (Filtration if cycle_reps else BoundaryMatrix)(L, 'alpha', True)
        return G, {G.index(L(F[i])) for i in R}
