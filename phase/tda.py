from phase.base import DataTransformation
from phase.util import format_float

from phase.plot.mpl import PersistencePlot

from phase.topology.persist import DiagramBase, Diagram

import numpy.linalg as la
import numpy as np


class PersistenceData(DataTransformation, PersistencePlot):
    module = 'persist'
    def __init__(self, input_data, parallel, verbose, *args, **kwargs):
        DataTransformation.__init__(self, input_data, parallel, verbose, *args, **kwargs)
        PersistencePlot.__init__(self)

class Persistence(PersistenceData):
    args = ['delta', 'coh'] + PersistenceData.args
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'base'
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
    def __init__(self, input_data, delta, coh, parallel, verbose):
        self.delta, self.coh = input_data.limits.max() * delta, coh
        PersistenceData.__init__(self, input_data, parallel, verbose, delta, coh)
    def __call__(self, K, verbose):
        F, R = K.get_filtration(self.delta, self.limits, False)
        dgm = DiagramBase(F.get_range(R), self.coh)
        # dgm._clearing_reduce(F, R, verbose)
        dgm._phcol_reduce(F, R, verbose)
        return dgm.get_diagram(F)

class PersistenceReps(Persistence):
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'representative'
    def run(self, *args, **kwargs):
        self.chain_data = Persistence.run(self, *args, **kwargs)
        return [d.get_diagram() for d in self.chain_data]
    def __call__(self, K, verbose):
        F, R = K.get_filtration(self.delta, self.limits, True)
        return Diagram(F, R, self.coh, verbose)
