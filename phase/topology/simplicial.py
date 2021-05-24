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
    def get_relative(self, delta, limits):
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



# class STNode:
#     __slots__ = ['label', 'data', 'parent', 'children', 'dim', 'simplex']
#     def __init__(self, label, parent=None, **kwargs):
#         self.label, self.data, self.parent = label, kwargs, parent
#         self.dim = 0 if parent is None else self.parent.dim + 1
#         self.children = {}
#         if parent is not None:
#             parent.add_child(self)
#         # self.simplex = self.get_simplex()
#     def get_children(self):
#         return list(self.children.values())
#     def get_simplex(self):
#         if self.dim == 0:
#             return (self.label,)
#         return self.parent.get_simplex() + (self.label,)
#     def is_simplex(self, s):
#         if self.label == s[-1]:
#             return (not self.dim
#                 or self.parent.is_simplex(s[:-1]))
#         return False
#     def add_child(self, other):
#         self.children[other.label] = other
#     def __eq__(self, other):
#         return self.label == other.label
#     def __hash__(self):
#         return self.label
#     def __getitem__(self, l):
#         return self.children[l]
#     def __repr__(self):
#         return str(self.get_simplex())
#     def __iter__(self):
#         if self.dim == 0:
#             yield self.label
#         else:
#             yield from self.parent
#     def is_face(self, s):
#         if len(s)-1 > self.dim:
#             return False
#         elif not s and self.dim < 2:
#             return True
#         elif self.label == s[-1]:
#             return not self.dim or self.parent.is_face(s[:-1])
#         elif self.dim and self.parent.label == s[-1]:
#             return self.parent.is_face(s)
#         return False
#
#
#
# class SimplexTree:
#     __slots__ = ['dim', 'tree']
#     def __init__(self, dim):
#         self.dim = dim
#         self.tree = {d : {} for d in range(dim+1)}
#     def __iter__(self):
#         for d,S in self.tree.items():
#             for s in S.values():
#                 yield from s
#     def add_new(self, s, **kwargs):
#         return self.add(STNode(s[-1], self.prefix(s), **kwargs))
#     def add(self, s):
#         if not s.label in self.tree[s.dim]:
#             self.tree[s.dim][s.label] = [s]
#         else:
#             self.tree[s.dim][s.label].append(s)
#         return s
#     def root(self, v):
#         return self.tree[0][v][0]
#     def prefix(self, s, p=None):
#         if len(s) > 1:
#             p = self.root(s[0]) if p is None else p[s[0]]
#             return self.prefix(s[1:], p)
#         return p
#     def get_node(self, s):
#         if len(s) > 1:
#             return self.prefix(s)[s[-1]]
#         return self.root(s[0])
#     def cofaces(self, s):
#         dim = len(s) - 1
#         cofaces = self.get_node(s).get_children()
#         if dim+1 in self.tree and s[-1] in self.tree[dim+1]:
#             cofaces += [c for c in self.tree[dim+1][s[-1]] if c.is_face(s)]
#         return cofaces
#     def faces(self, s):
#         return [self[s[:i]+s[i+1:]] for i in range(len(s))]
#     # def add_new(self, s, data):
#     #     l = vertices[-1]
#     #     if len(vertices) > 1:
#     #         parent = self.prefix(s)
#     #         s = STNode(s[-1], data, self.prefix(s))
#     #         if not l in self.tree[s.dim]:
#     #             self.tree[s.dim][l] = []
#     #         self.tree[s.dim][l].append(s)
#     #         return s
#     #     s = STNode(l, data)
#     #     self.tree[0][l] = [s]
#     #     return s
#
#     # def cofaces(self, s):
#     #     l = s[-1]
#     #     cofaces = []
#     #     for c in self.tree[len(s)][l]:
#     #         f = [c]
#     #         p = c.parent
#     #         for t in s[:-1:-1]:
#     #             if p.label == t:
#     #                 f = [p] + f
#     #             elif p.parent.label == t:
#     #                 f = [p.parent, p] + f
# #
# class STComplex(SimplexTree):
#     def get_sequence(self, key, reverse=False):
#         r = -1 if reverse else 1
#         return sorted(self, key=lambda s: (r * s.data[key], s.dim, s.label))
#     # def items(self):
#     #     yield from self.tree.items()
#     # def keys(self):
#     #     yield from self
#     # def values(self):
#     #     yield from self
#     def __len__(self):
#         return sum(len(s) for _,s in self.tree.items())
#     def __call__(self, s):
#         return s.get_simplex()
#     def __getitem__(self, dim):
#         for _,S in self.tree[dim].values():
#             yield from S
#     # def __contains__(self, s):
#     #     return s in self.smap
#     # def __repr__(self):
#     #     return ''.join(['%d:\t%d cells\n' % (d, len(S)) for d,S in self.items()])
#     # def add_new(self, s, faces, dim, **kwargs):
#     #     # if dim <= self.dim:
#     #     return self.add(Cell(s, map(self, faces), dim, **kwargs))
#     def orient_face(self, s):
#         return s
#
#
# class AlphaComplex(STComplex):
#     __slots__ = ['dim', 'tree', 'P', 'key']
#     def __init__(self, P, key='alpha', dim=None, verbose=False):
#         self.P, self.key = P, key
#         dim = P.shape[-1] if dim is None else dim
#         STComplex.__init__(self, dim)
#         A = diode.fill_alpha_shapes(P.astype(float), True)
#         for s, f in (tqdm(A, desc='[ alpha complex') if verbose else A):
#             self.add_new(sorted(s), **{key : f})
#     def get_relative(self, delta, limits):
#         if delta > 0:
#             Q = {i for i,p in enumerate(self.P) if is_boundary(p, delta, limits)}
#             return {s.get_simplex() for s in self if all(v in Q for v in s)}
#         return set()
