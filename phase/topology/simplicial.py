from phase.topology.cells import Cell, CellComplex
from phase.topology.chains import BoundaryMatrix, Filtration
from phase.util import stuple, is_boundary
from phase.geometry import tet_circumcenter


from itertools import combinations
from scipy.spatial import Delaunay
import numpy.linalg as la
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
    __slots__ = ['dim', 'cells', 'smap', 'P', 'key']
    def __init__(self, P, key='alpha', dim=None, verbose=False):
        self.P, self.key = P, key
        dim = P.shape[-1] if dim is None else dim
        SimplicialComplex.__init__(self, dim)
        A = diode.fill_alpha_shapes(P.astype(float), True)
        for s, f in (tqdm(A, desc='[ alpha complex') if verbose else A):
            self.add_new(s, **{key : f})
        # self.boundary = {s for s in self[2] if len(s.cofaces) == 1}
    #     dela = Delaunay(P)
    #     self.edge_lengths = {}
    #     A = dela.simplices
    #     for s in (tqdm(A, desc='[ alpha complex') if verbose else A):
    #         self.fill_faces(stuple(s))
    # def circumradius(self, s, f):
    #     if not len(f):
    #         return 0
    #     elif len(f) == 2:
    #         d = la.norm(self.P[f[0]] - self.P[f[1]])
    #         self.edge_lengths[s] = d
    #         return  d ** 2 / 4
    #     elif len(f) == 3:
    #         a, b, c = [self.edge_lengths[t] for t in f]
    #         return (a*b*c / np.sqrt((a+b+c)*(b+c-a)*(c+a-b)*(a+b-c))) ** 2 / 4
    #     elif len(f) == 4:
    #         # i,j,k,l = s
    #         # a,b,c = [self.edge_lengths[i,v] for v in s[1:]]
    #         # A,B,C = [self.edge_lengths[u,v] for u,v in ((j,k),(j,l),(k,l))]
    #         # x,y,z,w = [self.P[u] for u in s]
    #         # V = abs(np.dot((x - w), np.cross((y - w),(z - w)))) / 6
    #         # n = abs((a*A+b*B+c*C)*(a*A+b*B-c*C)*(a*A-b*B+c*C)*(b*B-a*A+c*C))
    #         # if n <= 0:
    #         #     print(n)
    #         # return (np.sqrt(n) / 24*V) ** 2 / 4
    #         return la.norm(tet_circumcenter(self.P[list(s)]) - self.P[s[0]]) ** 2 / 4
    #         # return r ** 2 / 4
    # def fill_faces(self, s):
    #     if s in self:
    #         return self(s)
    #     faces = [self.fill_faces(s[:i]+s[i+1:]) for i in range(len(s))] if len(s) > 1 else []
    #     return self.add(Simplex(s, faces, **{self.key : self.circumradius(s, faces)}))
    #     # return self.add_new(s, faces, **{self.key : alpha})
    # def closure(self, S):
    #     return {t for s in S for t in self.closure(self(s).faces)}.union(S)
    #     # for s in S:
    #     #     s = self(s)
    #     #     if s.dim > 1:
    #     #         return {t for f in s.faces for t in closure(t)}.union(s.faces)
    #     #     return {tuple(s)}
    def get_relative(self, delta, limits):
        # return self.closure({s for s in self[2] if len(s.cofaces) == 1})
        if delta > 0:
            Q = {i for i,p in enumerate(self.P) if is_boundary(p, delta, limits)}
            return {s for s in self.values() if all(v in Q for v in s)}
        return set()

class DioComplex(SimplicialComplex):
    __slots__ = ['dim', 'cells', 'smap', 'key']
    def __init__(self, simplices, key, dim):
        self.key = key
        SimplicialComplex.__init__(self, dim)
        for s in simplices:
            self.add_new(list(s), map(self, s.boundary()), **{self.key : s.data})
