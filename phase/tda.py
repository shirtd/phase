from phase.base import DataTransformation
from phase.util import format_float

from phase.plot.mpl import PersistencePlot

from phase.topology.persist import Diagram

import numpy.linalg as la
import numpy as np


class PersistenceData(DataTransformation, PersistencePlot):
    module = 'persist'
    def __init__(self, input_data, parallel, verbose, *args, **kwargs):
        DataTransformation.__init__(self, input_data, parallel, verbose, *args, **kwargs)
        PersistencePlot.__init__(self)

class Persistence(PersistenceData):
    args = ['delta', 'coh', 'clearing'] + PersistenceData.args
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'pers'
    @classmethod
    def make_name(cls, input_name, delta, coh, *args, **kwargs):
        name = '%s_%s' % (input_name, cls.get_prefix())
        if delta > 0:
            d = {'delta' : delta}
            s = ['%s%s' % (l,format_float(v)) for l,v in d.items() if v > 0]
            name = '-'.join([name] + s)
        if coh:
            name += '-coh'
        return name
    @classmethod
    def make_title(cls, input_title, delta, coh, *args, **kwargs):
        title = '%s %s' % (input_title, cls.get_prefix())
        if delta > 0:
            d = {'delta' : delta}
            s = ['%s=%g' % (l,v) for l,v in d.items() if v > 0]
            title = '%s (%s)' % (title, ','.join(s))
        if coh:
            title += '-coh'
        return title
    def __init__(self, input_data, delta, coh, clearing, parallel, verbose):
        self.delta, self.coh, self.clearing = input_data.limits.max() * delta, coh, clearing
        PersistenceData.__init__(self, input_data, parallel, verbose, delta, coh)
    def __call__(self, F, verbose):
        R = F.get_relative(self.delta, self.limits)
        return Diagram(F, R, self.coh, False, self.clearing, verbose).diagram

class PersistenceReps(Persistence):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return '%s-rep' % (Persistence.get_prefix(cls, *args, **kwargs))
    def run(self, input_data, *args, **kwargs):
        self.reps = Persistence.run(self, input_data, *args, **kwargs)
        return [H.diagram for H in self.reps]
    def __call__(self, F, verbose):
        R = F.get_relative(self.delta, self.limits)
        return Diagram(F, R, self.coh, True, self.clearing, verbose)

def pers_cls(args):
    return (PersistenceReps if args.reps
        else Persistence)



# class CachedPersistenceData(CachedDataTransformation, PersistenceData):
#     module = 'persist'
#     def __init__(self, input_data, frames, cache, parallel, verbose, *args, **kwargs):
#         CachedDataTransformation.__init__(self, input_data, frames, parallel, verbose, *args, **kwargs)
#         PersistencePlot.__init__(self)
#
# class CachedPersistence(CachedPersistenceData, Persistence):
#     args = ['delta', 'coh', 'clearing'] + CachedPersistenceData.args
#     def __init__(self, input_data, delta, coh, clearing, frames, cache, parallel, verbose):
#         self.delta, self.coh, self.clearing = input_data.limits.max() * delta, coh, clearing
#         CachedPersistenceData.__init__(self, input_data, frames, parallel, verbose, delta, coh)
#     def __call__(self, F, verbose):
#         pass
#
# class CachedPersistenceReps(CachedPersistenceData, PersistenceReps):
#     args = ['delta', 'coh', 'clearing'] + CachedPersistenceData.args
#     def __init__(self, input_data, delta, coh, clearing, frames, cache, parallel, verbose):
#         self.delta, self.coh, self.clearing = input_data.limits.max() * delta, coh, clearing
#         CachedPersistenceData.__init__(self, input_data, frames, parallel, verbose, delta, coh)
#     def run(self, input_data, *args, **kwargs):
#         pass
