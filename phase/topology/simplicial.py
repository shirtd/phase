from phase.util import stuple
from phase.topology.cells import Cell, CellComplex

from itertools import combinations
from tqdm import tqdm
import numpy as np
import diode


class Simplex(Cell):
    def __init__(self, vertices, faces, **kwargs):
        Cell.__init__(self, vertices, faces, len(vertices)-1, **kwargs)
    def star(self, i):
        return [(i,) + f for f in self.faces] if self.dim > 0 else [(i,)]
    def face_it(self):
        for i in range(self.dim+1):
            yield stuple(self[:i]+self[i+1:])

class SimplicialComplex(CellComplex):
    def __repr__(self):
        return ''.join(['%d:\t%d simplices\n' % (d, len(S)) for d,S in self.items()])
    def add_new(self, s, faces=None, **kwargs):
        if faces is None:
            faces = [tuple(s[:i]+s[i+1:]) for i in range(len(s))]
        return self.add(Simplex(s, map(self, faces), **kwargs))


class AlphaComplex(SimplicialComplex):
    def __init__(self, P, key='alpha'):
        self.P, self.key = P, key
        SimplicialComplex.__init__(self, P.shape[1])
        for s, f in diode.fill_alpha_shapes(P):
            self.add_new(s, **{key : f})

class DioComplex(SimplicialComplex):
    def __init__(self, simplices, key, dim):
        self.key = key
        SimplicialComplex.__init__(self, dim)
        for s in simplices:
            self.add_new(list(s), map(self, s.boundary()), **{self.key : s.data})
