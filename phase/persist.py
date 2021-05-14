import numpy as np
from tqdm import tqdm
from phase.simplicial import Chain

class Diagram:
    def __init__(self, F, D, pairs=None, unpairs=None):
        self.F, self.D = F, D
        self.pairs = {} if pairs is None else pairs
        self.unpairs = set() if unpairs is None else unpairs
    def get_pairs(self):
        return list(sorted(self.pairs.items(), key=lambda p: abs(self.data(p[0]) - self.data(p[1]))))
    def get_pair(self, i):
        return np.array([self.data(self.F[i]), self.data(self.F[self[i]])])
    def persistence(self, i):
        b,d = self.get_pair(i)
        return d - b
    # def persistence(self, s):
    #     if isinstance(s, ColumnBase):
    #         s = s.simplex
    #     if s in self.unpairs:
    #         return np.inf
    #     return abs(self.F(s) - self.F(self[s]))
    def items(self):
        yield from self.pairs
    def data(self, s):
        if s is None:
            return np.inf
        return s.data[self.F.key]
    def __getitem__(self, s):
        if s in self.pairs:
            return self.pairs[s]
        return None
    def add_pair(self, low, i):
        if low is not None:
            self.pairs[low] = i
            if low in self.unpairs:
                self.unpairs.remove(low)
            if i in self.unpairs:
                self.unpairs.remove(i)
        elif not i in self.pairs:
            self.unpairs.add(i)
    def try_pair(self, i, R=set()):
        low = self.D[i].get_pivot(R)
        while low in self.pairs:
            self.D[i] += self.D[self.pairs[low]]
            low = self.D[i].get_pivot(R)
        return low
    def get_diagram(self, invert=False):
        diagrams = {d : [] for d in range(self.F.dim+1)}
        for i,j in self.pairs.items():
            if invert:
                j,i = i,j
            b, d = self.F.get_data(i), self.F.get_data(j)
            if b < d:
                diagrams[self.F[i].dim].append([b, d])
        for i in self.unpairs:
            b = self.F.get_data(i)
            diagrams[self.F[i].dim].append([b, np.inf])
        return [np.array(diagrams[d]) for d in sorted(diagrams.keys())]


def phcol(F, R=set(), upper=np.inf, lower=-np.inf):
    rng = F.get_range(R, upper, lower)
    D = F.get_boundary(rng)
    dgm = Diagram(F, D)
    for i in rng:
        low = dgm.try_pair(i, R)
        dgm.add_pair(low, i)
    return dgm

def pcoh(F, R=set(), upper=np.inf, lower=-np.inf):
    _rng = F.get_range(R, upper, lower)
    D = F.get_coboundary(_rng)
    dgm = Diagram(F, D)
    for dim in range(F.dim+1):
        rng = [i for i in _rng if F[i].dim == dim and not i in dgm.pairs]
        for i in reversed(rng):
            dgm.try_pair(i, R)
    return dgm
