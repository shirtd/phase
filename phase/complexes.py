from phase.topology.cells import DualComplex
from phase.topology.simplicial import AlphaComplex
from phase.base import DataTransformation

from phase.topology.chains import BoundaryMatrix

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

class AlphaComplexData(ComplexData):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'alpha'
    def __call__(self, d, verbose):
        K = AlphaComplex(d, 'alpha', self.dim, verbose)
        return BoundaryMatrix(K, 'alpha', False)

class VoronoiComplexData(ComplexData):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'dual'
    def __call__(self, d, verbose):
        K = AlphaComplex(d, 'alpha', self.input_dim, verbose)
        G = DualComplex(K, 'alpha', self.dim, verbose)
        return BoundaryMatrix(G, 'alpha', True)
