import numpy as np

class BoundaryColumn:
    @classmethod
    def sum(cls, *chains):
        return sum(*chains, cls())
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

class CoChain(BoundaryColumn):
    def __init__(self, simplices=set(), boundary=[]):
        BoundaryColumn.__init__(self, simplices, boundary)
    def __add__(self, other):
        simplices = self.simplices ^ other.simplices
        boundary = []
        i, j = 0, 0
        while i < self.m and j < other.m:
            if i < self.m and self.boundary[i] > other.boundary[j]:
                while i < self.m and self.boundary[i] > other.boundary[j]:
                    boundary += [self.boundary[i]]
                    i += 1
            elif j < other.m and other.boundary[j] > self.boundary[i]:
                while j < other.m and other.boundary[j] > self.boundary[i]:
                    boundary += [other.boundary[j]]
                    j += 1
            else:
                i += 1
                j += 1
        if i < self.m:
            boundary += self.boundary[i:]
        elif j < other.m:
            boundary += other.boundary[j:]
        return CoChain(simplices, boundary)

class Filtration:
    def __init__(self, complex, key='max', reverse=False):#, test=lambda a,b: a < b):
        self.complex, self.dim, self.n = complex, complex.dim, len(complex)
        self.key, self.reverse = key, reverse
        self.sequence = sorted(complex.values(), key=self.forder)
        self.imap = {s : i for i, s in enumerate(self.sequence)}
    def forder(self, s):
        return ((-1 if self.reverse else 1) * s.data[self.key], s)
    def __len__(self):
        return len(self.sequence)
    def __iter__(self):
        for s in self.sequence:
            yield s
    def __getitem__(self, i):
        return self.sequence[i]
    def __call__(self, s):
        if isinstance(s, int):
            return self(self[s])
        return self.complex.smap[s](self.key)
    def index(self, s):
        return self.imap[s]
    def get_range(self, relative=set(), upper=np.inf, lower=-np.inf): # optimize: thresh/index map
        return [i for i,s in enumerate(self) if not i in relative and lower <= self(s) < upper]
    def sort_faces(self, s, reverse=False):
        return list(sorted([self.index(f) for f in s.faces], reverse=reverse))
    def sort_cofaces(self, s, reverse=True):
        return list(sorted([self.index(f) for f in s.cofaces], reverse=reverse))
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
    def get_matrix(self, rng, coh=False):
        return self.get_coboundary(rng) if coh else self.get_boundary(rng)
    def get_boundary(self, rng):
        return {i : self.as_chain(i) for i in rng}
    def get_coboundary(self, rng):
        return {i : self.as_cochain(i) for i in rng}
