import numpy as np

class ColumnBase:
    @classmethod
    def sum(cls, *chains):
        return sum(*chains, cls())
    def __init__(self, boundary):
        self.boundary = boundary
        self.m = len(self.boundary)
    def get_pivot(self, relative=set()):
        if self.m == 0:
            return None
        if not relative:
            return self.boundary[-1]
        for i in self.boundary[::-1]:
            if not i in relative:
                return i
        return None
    def _add_boundary(self, other):
        boundary = []
        i, j = 0, 0
        while i < self.m and j < other.m:
            if i < self.m and self._cmp(self.boundary[i], other.boundary[j]):
                boundary += [self.boundary[i]]
                i += 1
                while i < self.m and self._cmp(self.boundary[i], other.boundary[j]):
                    boundary += [self.boundary[i]]
                    i += 1
            elif j < other.m and other._cmp(other.boundary[j], self.boundary[i]):
                boundary += [other.boundary[j]]
                j += 1
                while j < other.m and other._cmp(other.boundary[j], self.boundary[i]):
                    boundary += [other.boundary[j]]
                    j += 1
            else:
                i += 1
                j += 1
        if i < self.m:
            boundary += self.boundary[i:]
        elif j < other.m:
            boundary += other.boundary[j:]
        return boundary
    def __add__(self, other):
        return type(self)(self._add_boundary(other))

class Boundary(ColumnBase):
    def _cmp(self, a, b):
        return a < b

class CoBoundary(ColumnBase):
    def _cmp(self, a, b):
        return a > b

class Column(ColumnBase):
    def __init__(self, simplices=set(), boundary=[]):
        self.simplices = simplices
        self.n = len(self.simplices)
        ColumnBase.__init__(self, boundary)
    def __add__(self, other):
        simplices = self.simplices ^ other.simplices
        boundary = self._add_boundary(other)
        return type(self)(simplices, boundary)
    def __len__(self):
        return len(self.simplices)
    def __iter__(self):
        for s in self.simplices:
            yield s
    def __repr__(self):
        return '+'.join([str(s) for s in self])

class Chain(Column, Boundary):
    def __repr__(self):
        return 'Chain(%s)' % '+'.join([str(s) for s in self])

class CoChain(Column, CoBoundary):
    def __repr__(self):
        return 'CoChain(%s)' % '+'.join([str(s) for s in self])

class BoundaryMatrix:
    def __init__(self, K, key, reverse):
        self.sequence = K.get_sequence(key, reverse)
        self.dim, self.key, self.reverse = K.dim, key, reverse
        self.imap = {s : i for i, s in enumerate(self)}
    def __len__(self):
        return len(self.sequence)
    def __iter__(self):
        for s in self.sequence:
            yield s
    def __getitem__(self, i):
        return self.sequence[i]
    def index(self, s):
        return self.imap[s]
    def sort_faces(self, s, reverse=False):
        return sorted([self.index(f) for f in s.faces], reverse=False)
    def sort_cofaces(self, s, reverse=True):
        return sorted([self.index(f) for f in s.cofaces], reverse=True)
    def as_chain(self, s):
        s = self[s] if isinstance(s, int) else s
        return Boundary(self.sort_faces(s))
    def as_cochain(self, s):
        s = self[s] if isinstance(s, int) else s
        return CoBoundary(self.sort_cofaces(s))
    def get_boundary(self, rng):
        return {i : self.as_chain(i) for i in rng}
    def get_coboundary(self, rng):
        return {i : self.as_cochain(i) for i in rng}
    def get_matrix(self, rng, coh=False):
        return self.get_coboundary(rng) if coh else self.get_boundary(rng)
    def get_range(self, relative=set()):
        return [i for i,s in enumerate(self) if not i in relative]

class Filtration(BoundaryMatrix):
    def __init__(self, K, key='max', reverse=False):
        BoundaryMatrix.__init__(self, K, key, reverse)
        self.K = K
    def __call__(self, s):
        if isinstance(s, int):
            return self(self[s])
        return self.K.smap[s](self.key)
    def as_chain(self, s):
        s = self[s] if isinstance(s, int) else s
        return Chain({s}, self.sort_faces(s))
    def as_cochain(self, s):
        s = self[s] if isinstance(s, int) else s
        return CoChain({s}, self.sort_cofaces(s))
    def boundary(self, chain):
        if isinstance(chain, Chain):
            return Chain.sum(self.as_chain(i) for i in chain.boundary)
        return CoChain.sum(self.as_cochain(i) for i in chain.boundary)
