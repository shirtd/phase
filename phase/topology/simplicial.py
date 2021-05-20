from phase.topology.cells import Cell, CellComplex
from phase.topology.chains import BoundaryMatrix, Filtration
from phase.util import stuple, is_boundary


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
            faces = [stuple(s[:i]+s[i+1:]) for i in range(len(s))]
        return self.add(Simplex(s, map(self, faces), **kwargs))

class AlphaComplex(SimplicialComplex):
    def __init__(self, P, key='alpha', dim=None, verbose=False):
        self.P, self.key = P, key
        dim = P.shape[-1] if dim is None else dim
        SimplicialComplex.__init__(self, dim)
        A = diode.fill_alpha_shapes(P.astype(float), True)
        for s, f in (tqdm(A, desc='[ alpha complex') if verbose else A):
            self.add_new(s, **{key : f})
    def get_boundary(self, F, delta, limits):
        if delta > 0:
            Q = {i for i,p in enumerate(self.P) if is_boundary(p, delta, limits)}
            return {i for i,s in enumerate(F) if all(v in Q for v in s)}
        return set()
    def get_filtration(self, delta, limits, cycle_reps=True):
        F = (Filtration if cycle_reps else BoundaryMatrix)(self, self.key, False)
        return F, self.get_boundary(F, delta, limits)

class DioComplex(SimplicialComplex):
    def __init__(self, simplices, key, dim):
        self.key = key
        SimplicialComplex.__init__(self, dim)
        for s in simplices:
            self.add_new(list(s), map(self, s.boundary()), **{self.key : s.data})
