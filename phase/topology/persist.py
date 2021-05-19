from phase.util import diff, identity

from tqdm import tqdm
import numpy as np


class Diagram:
    def __init__(self, F, R=set(), coh=False, upper=np.inf, lower=-np.inf, clearing=False):
        self.F, self.R, self.coh, self.thresh = F, R, coh, (lower, upper)
        self.rng = F.get_range(R, upper, lower)
        self.D = F.get_matrix(self.rng, coh)
        self.pairs, self.pmap = {}, {}
        self.unpairs = set(self.rng)
        self.reduce(clearing)
    def reduce(self, clearing=False):
        if clearing:
            dit = range(self.F.dim+1)
            for dim in (dit if self.coh else reversed(dit)):
                rng = [i for i in self.rng if self.F[i].dim == dim and not i in self]
                for i in (reversed(rng) if self.coh else rng):
                    low = self.try_pair(i)
                    if low is not None:
                        self[low] = i
        else:
            for i in (reversed(self.rng) if self.coh else self.rng):
                low = self.try_pair(i)
                if low is not None:
                    self[low] = i
        if self.coh:
            self.pairs, self.pmap = self.pmap, self.pairs
    def is_relative(self, i):
        if not isinstance(i, int):
            i = self.F.index(i)
        return i in self.R
    def items(self):
        return self.pairs.items()
    def keys(self):
        return self.pairs.keys()
    def values(self):
        return self.pairs.values()
    def persistence(self, i):
        return diff(self(i))
    def __contains__(self, i):
        if not isinstance(i, int):
            i = self.F[i]
        return i in self.pairs
    def __call__(self, i):
        if not isinstance(i, int):
            i = self.F.index(i)
        if i in self.pairs:
            p = np.array([self.F(i), self.F(self[i])])
            return p[::-1] if self.F.reverse else p
        return np.array([self.F(i), np.inf])
    def __getitem__(self, i):
        if i in self.pairs:
            return self.pairs[i]
        return None
    def __setitem__(self, b, d):
        self.pairs[b] = d
        self.pmap[d] = b
        self.unpairs.remove(b)
        self.unpairs.remove(d)
    def try_pair(self, i):
        low = self.D[i].get_pivot(self.R)
        while low in self.pairs:
            self.D[i] += self.D[self.pairs[low]]
            low = self.D[i].get_pivot(self.R)
        return low
    def get_diagram(self):
        dgms = [np.ndarray((0,2), dtype=float) for d in range(self.F.dim+1)]
        for i,j in self.items():
            p = self(i)
            if p[0] < p[1]:
                dgms[self.F[i].dim] = np.vstack((dgms[self.F[i].dim], p))
        for i in self.unpairs:
            dgms[self.F[i].dim] = np.vstack((dgms[self.F[i].dim], self(i)))
        return dgms
