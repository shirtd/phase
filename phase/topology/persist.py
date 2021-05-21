from phase.util import diff, identity

from functools import reduce
from tqdm import tqdm
import numpy as np


class Diagram:
    def __init__(self, F, R=set(), coh=False, cycle_reps=False, clearing=False, verbose=False):
        self.sequence, self.n = F.get_range(R, coh), len(F) - len(R)
        self.R, self.coh, self.dim = R, coh, F.dim
        self.unpairs = reduce(lambda a,b: a.union(b), self.sequence, set())
        self.pairs, self.copairs = {}, {}
        self.D = F.get_matrix(self.sequence, coh, cycle_reps)
        self.reduce(clearing, verbose)
        self.diagram, self.fmap = self.get_diagram(F)
    def __iter__(self):
        for seq in self.sequence:
            yield from seq
    def __len__(self):
        return self.n
    def __setitem__(self, b, d):
        if self.coh:
            b, d = d, b
        self.pairs[b] = d
        self.copairs[d] = b
        self.unpairs.remove(b)
        self.unpairs.remove(d)
    def _pair(self, low):
        pairs = self.copairs if self.coh else self.pairs
        return pairs[low] if low in pairs else None
    def _paired(self, low):
        return low is not None and low in (self.copairs if self.coh else self.pairs)
    def reduce(self, clearing=False, verbose=False, desc='[ persist'):
        for i in (tqdm(self, total=self.n, desc=desc) if verbose else self):
            if not (clearing or self._paired(i)):
                low = self.D[i].get_pivot(self.R)
                while self._paired(low):
                    self.D[i] += self.D[self._pair(low)]
                    low = self.D[i].get_pivot(self.R)
                if low is not None:
                    self[low] = i
    def __call__(self, i):
        if i in self.fmap:
            return self.fmap[i]
        return None
    def __getitem__(self, i):
        return self.pairs[i] if i in self.pairs else None
    def __contains__(self, i):
        return i is not None and i in self.pairs
    def items(self):
        yield from self.pairs.items()
    def keys(self):
        yield from self.pairs.keys()
    def values(self):
        yield from self.pairs.values()
    def is_relative(self, i):
        return i in self.R
    def get_diagram(self, F):
        dgms, fmap = [np.ndarray((0,2), dtype=float) for d in range(self.dim+1)], {}
        for i,j in self.items():
            p = np.array([F[i].data[F.key], F[self[i]].data[F.key]])
            if F.reverse:
                p = p[::-1]
            fmap[i] = p
            if p[0] < p[1]:
                dgms[F[i].dim] = np.vstack((dgms[F[i].dim], p))
        for i in self.unpairs:
            p = np.array([F[i].data[F.key], np.inf])
            dgms[F[i].dim] = np.vstack((dgms[F[i].dim], p))
            fmap[i] = p
        return dgms, fmap

# class Diagram(DiagramBase):
#     def __init__(self, F, R=set(), coh=False, clearing=False, verbose=False):
#         self.F, self.R = F, R
#         DiagramBase.__init__(self, F.get_range(R), coh)
#         self.D = (self._clearing_reduce if clearing else self._phcol_reduce)(F, R, True, verbose)
#     def __contains__(self, i):
#         if not isinstance(i, int):
#             i = self.F[i]
#         return DiagramBase.__contains__(self, i)
#     def __call__(self, i):
#         if not isinstance(i, int):
#             i = self.F.index(i)
#         if i in self.pairs:
#             p = np.array([self.F(i), self.F(self[i])])
#             return p[::-1] if self.F.reverse else p
#         return np.array([self.F(i), np.inf])
#     def is_relative(self, i):
#         if not isinstance(i, int):
#             i = self.F.index(i)
#         return i in self.R
#     def persistence(self, i):
#         return diff(self(i))
#     def get_diagram(self):
#         return DiagramBase.get_diagram(self, self.F)
