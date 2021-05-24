from phase.topology.cells import DualComplex
from phase.topology.simplicial import AlphaComplex
from phase.base import DataTransformation

from phase.topology.chains import BoundaryMatrix

import numpy.linalg as la
import numpy as np


class FiltrationData(DataTransformation):
    module = 'filt'
    args = ['dim'] + DataTransformation.args
    @classmethod
    def make_name(cls, input_name, dim, *args, **kwargs):
        return '%s_%s' % (input_name, cls.get_prefix())
        # dstr = '' if dim == input_data.dim else '%dD' % dim
        # return '%s_%s%s' % (input_data.name, cls.get_prefix(), dstr)
    @classmethod
    def make_title(cls, input_title, dim, *args, **kwargs):
        return '%s %s' % (input_title, cls.get_prefix())
        # dstr = '' if dim == input_data.dim else '%dD' % dim
        # return '%s %s %s' % (input_data.title, cls.get_prefix(), dstr)
    def __init__(self, input_data, dim, parallel, verbose, *args, **kwargs):
        self.dim, self.input_dim = dim, input_data.dim
        DataTransformation.__init__(self, input_data, parallel, verbose, dim, *args, **kwargs)

class AlphaFiltrationData(FiltrationData):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'alpha'
    def __call__(self, d, verbose):
        K = AlphaComplex(d, 'alpha', self.dim, verbose)
        return BoundaryMatrix(K, 'alpha', False)

class VoronoiFiltrationData(FiltrationData):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'dual'
    def __call__(self, d, verbose):
        K = AlphaComplex(d, 'alpha', self.input_dim)
        G = DualComplex(K, 'alpha', self.dim, verbose)
        return BoundaryMatrix(G, 'alpha', True)

def filt_cls(args):
    return (VoronoiFiltrationData if args.dual
        else AlphaFiltrationData)


# class CachedFiltrationData(CachedDataTransformation, FiltrationData):
#     args = ['dim'] + CachedDataTransformation.args
#     def __init__(self, input_data, dim, frames, cache, parallel, verbose, *args, **kwargs):
#         self.dim, self.input_dim = dim, input_data.dim
#         CachedDataTransformation.__init__(self, input_data, frames, cache, parallel, verbose, dim, *args, **kwargs)
#
# class CachedAlphaFiltrationData(CachedFiltrationData, AlphaFiltrationData):
#     def __call__(self, d, verbose):
#         pass
#
# class CachedVoronoiFiltrationData(CachedFiltrationData, VoronoiFiltrationData):
#     def __call__(self, d, verbose):
#         pass
