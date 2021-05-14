from phase.util import stuple
from tqdm import tqdm
import numpy as np

class Simplex(tuple):
    def __new__(cls, vertices, faces=None, **kwargs):
        return tuple.__new__(cls, stuple(vertices))
    def __init__(self, vertices, faces=None, **kwargs):
        tuple.__init__(self)
        self.dim = len(self) - 1
        self.data = kwargs
        # self.cofaces = []
        if faces is not None:
            self.add_faces(faces)
    def items(self):
        yield from self.data.items()
    def add_faces(self, faces):
        self.faces = faces
        # for f in faces:
        #     f.add_coface(self)
    # def add_coface(self, coface):
    #     self.cofaces += [coface]
    def star(self, i):
        return [(i,) + f for f in self.faces] if self.dim > 0 else [(i,)]
    def __contains__(self, s):
        if isinstance(s, Simplex):
            return all(v in self for v in s)
        elif isinstance(s, int):
            return tuple.__contains__(self, s)
        return False
    def face_it(self):
        for i in range(self.dim+1):
            yield stuple(self[:i]+self[i+1:])

class BoundaryColumn:
    def __init__(self, simplices=set(), boundary=[]):
        self.simplices, self.boundary = simplices, boundary
        self.n, self.m = len(self.simplices), len(self.boundary)
    def __len__(self):
        return len(self.simplices)
    def __iter__(self):
        for s in self.simplices:
            yield s
    def get_pivot(self, relative=set()):
        if self.m == 0:
            return None
        if not relative:
            return self.boundary[-1]
        for i in self.boundary[::-1]:
            if not i in relative:
                return i
        return None
    def __repr__(self):
        return '+'.join([str(s) for s in self])

class Chain(BoundaryColumn): # set of simplices and sorted list of boundary indices
    @classmethod
    def sum(cls, *chains):
        return sum(*chains, cls())
    def __init__(self, simplices=set(), boundary=[]):
        BoundaryColumn.__init__(self, simplices, boundary)
    def __add__(self, other):
        simplices = self.simplices ^ other.simplices
        boundary = []
        i, j = 0, 0
        while i < self.m and j < other.m:
            if i < self.m and self.boundary[i] < other.boundary[j]:
                while i < self.m and self.boundary[i] < other.boundary[j]:
                    boundary += [self.boundary[i]]
                    i += 1
            elif j < other.m and other.boundary[j] < self.boundary[i]:
                while j < other.m and other.boundary[j] < self.boundary[i]:
                    boundary += [other.boundary[j]]
                    j += 1
            else:
                i += 1
                j += 1
        if i < self.m:
            boundary += self.boundary[i:]
        elif j < other.m:
            boundary += other.boundary[j:]
        return Chain(simplices, boundary)

# class CoChain(BoundaryColumn):
#     def __init__(self, simplices=set(), boundary=[]):
#         BoundaryColumn.__init__(self, simplices, boundary)
#     def __add__(self, other):
#         simplices = self.simplices ^ other.simplices
#         boundary = []
#         i, j = 0, 0
#         while i < self.m and j < other.m:
#             if i < self.m and self.boundary[i] > other.boundary[j]:
#                 while i < self.m and self.boundary[i] > other.boundary[j]:
#                     boundary += [self.boundary[i]]
#                     i += 1
#             elif j < other.m and other.boundary[j] > self.boundary[i]:
#                 while j < other.m and other.boundary[j] > self.boundary[i]:
#                     boundary += [other.boundary[j]]
#                     j += 1
#             else:
#                 i += 1
#                 j += 1
#         if i < self.m:
#             boundary += self.boundary[i:]
#         elif j < other.m:
#             boundary += other.boundary[j:]
#         return CoChain(simplices, boundary)

class SimplicialComplex:
    def __init__(self, dim):
        self.dim = dim
        self.simplices = {d : set() for d in range(self.dim+1)}
        self.smap = {} # map tuples to Simplex objects
    def items(self):
        yield from self.simplices.items()
    def __len__(self):
        return len(self.smap)
    def __getitem__(self, dim):
        return self.simplices[dim]
    def get_simplex(self, t):
        return self.smap[t]
    def add(self, s):
        self.simplices[s.dim].add(s)
        self.smap[s] = s
    def remove(self, s):
        s = self.smap[s]
        if s in self:
            self.simplices[s.dim].remove(s)
        del self.smap[s]
    def __contains__(self, s):
        return s in self.smap
    def __repr__(self):
        return ''.join(['%d:\t%d simplices\n' % (d, len(S)) for d,S in self.items()])

class DioComplex(SimplicialComplex):
    def __init__(self, simplices, key, dim):
        self.key = key
        SimplicialComplex.__init__(self, dim)
        for s in simplices:
            faces = [self.smap[stuple(f)] for f in s.boundary()]
            s = Simplex(list(s), faces, **{self.key : s.data})
            self.add(s)

class Filtration:
    def __init__(self, complex, key='max', reverse=False):#, test=lambda a,b: a < b):
        self.complex, self.key, self.dim, self.n = complex, key, complex.dim, len(complex)
        self.sequence = list(sorted(complex.smap.values(), key=lambda s: ((-1 if reverse else 1) * s.data[key], s)))
        self.imap = {s : i for i, s in enumerate(self.sequence)}
    def __len__(self):
        return len(self.sequence)
    def __iter__(self):
        for s in self.sequence:
            yield s
    def __getitem__(self, i):
        return self.sequence[i]
    def __call__(self, s):
        return self.complex.smap[s].data[self.key]
    def get_data(self, s):
        if isinstance(s, int):
            return self.get_data(self[s])
        return s.data[self.key]
    def index(self, s):
        return self.imap[s]
    def get_range(self, relative=set(), upper=np.inf, lower=-np.inf): # optimize: thresh/index map
        return [i for i,s in enumerate(self) if not i in relative and lower <= self.get_data(s) < upper]
    def sort_faces(self, s, reverse=False):
        return list(sorted([self.index(f) for f in s.faces], reverse=reverse))
    # def sort_cofaces(self, s, reverse=True):
    #     return list(sorted([self.index(f) for f in s.cofaces], reverse=reverse))
    def as_chain(self, s):
        s = self[s] if isinstance(s, int) else s
        return Chain({s}, self.sort_faces(s))
    def boundary(self, chain):
        return Chain.sum(self.as_chain(i) for i in chain.boundary)
    def get_boundary(self, rng):
        return {i : self.as_chain(i) for i in rng}
    # def get_coboundary(self, rng):
    #     return {i : CoChain({self[i]}, self.sort_cofaces(self[i])) for i in rng}
