from phase.util import stuple, to_path
from phase.geometry import tet_circumcenter

from functools import reduce
from tqdm import tqdm
import numpy as np


class Cell(tuple):
    def __new__(cls, vertices, *args, **kwargs):
        return tuple.__new__(cls, stuple(vertices))
    def __init__(self, vertices, faces, dim, **kwargs):
        tuple.__init__(self)
        self.dim, self.data = dim, kwargs
        self.faces, self.cofaces = [], []
        if self.dim > 0:
            for f in faces:
                self.faces.append(tuple(f))
                f.add_coface(self)
    def add_coface(self, coface):
        self.cofaces.append(tuple(coface))
    def items(self):
        yield from self.data.items()
    def __contains__(self, v):
        return tuple.__contains__(self, v)
    def __call__(self, s):
        if s in self.data:
            return self.data[s]
        return None

class CellComplex:
    def __init__(self, dim):
        self.dim = dim
        self.cells = {d : set() for d in range(dim+1)}
        self.smap = {}
    # def get_sequence(self, key, dim, reverse=False):
    #     r = -1 if reverse else 1
    #     if dim < self.dim:
    #         S = [self[dim] for dim in range(dim+1)]
    #         values = reduce(lambda a,b: a + list(b), S, [])
    #     else:
    #         values = self.values()
    #     return sorted(values, key=lambda s: (r * s.data[key], s))
    def get_sequence(self, key, reverse=False):
        r = -1 if reverse else 1
        return sorted(self.values(), key=lambda s: (r * s.data[key], s))
    def items(self):
        yield from self.cells.items()
    def keys(self):
        return self.smap.keys()
    def values(self):
        return self.smap.values()
    def __len__(self):
        return len(self.smap)
    def __call__(self, s):
        if s in self.smap:
            return self.smap[s]
        s = stuple(s)
        if s in self.smap:
            return self.smap[s]
    def __getitem__(self, s):
        return self.cells[s]
    def add(self, s):
        if s in self.smap:
            return self.smap[s]
        self.cells[s.dim].add(s)
        self.smap[tuple(s)] = s
        return s
    def remove(self, s):
        s = self.smap[s]
        if s in self:
            self.cells[s.dim].remove(s)
        del self.smap[s]
    def __contains__(self, s):
        return s in self.smap
    def __repr__(self):
        return ''.join(['%d:\t%d cells\n' % (d, len(S)) for d,S in self.items()])
    def orient_face(self, s):
        return s
    def add_new(self, s, faces, dim, **kwargs):
        return self.add(Cell(s, map(self, faces), dim, **kwargs))

class DualComplex(CellComplex):
    def __init__(self, K, key):
        CellComplex.__init__(self, K.dim)
        self.K, self.key = K, key
        T = sorted(K[3], key=lambda t: t.data[key], reverse=True)
        self.imap = {t : i for i,t in enumerate(T)}
        self.P = np.vstack([tet_circumcenter(K.P[list(t)]) for t in T])
        self.dmap, self.pmap = {}, {}
        for dim in reversed(range(self.dim+1)):
            for s in K[dim]:
                self.dmap[s] = self.add(self.get_dual(s))
                self.pmap[self.dmap[s]] = s
        self.nbrs = {i : set() for i,_ in enumerate(self[0])}
        for e in self[1]:
            if len(e) == 2:
                self.nbrs[e[0]].add(e[1])
                self.nbrs[e[1]].add(e[0])
    def __call__(self, s):
        return self.dmap[s]
    def get_dual(self, s):
        dim = self.dim - s.dim
        vs = self.get_vertices(s)
        faces = [self.dmap[f] for f in s.cofaces]
        return Cell(vs, faces, dim, **s.data)
    def get_vertices(self, s):
        s = self.K.smap[s]
        if s.dim < 3:
            return {v for f in s.cofaces for v in self.get_vertices(f)}
        return {self.imap[s]}
    def orient_face(self, s):
        return to_path({v for v in s}, self.nbrs)
