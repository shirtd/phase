from phase.util import diff, identity

from tqdm import tqdm
import numpy as np


class DiagramBase:
    def __init__(self, sequence, coh=False):
        self.sequence, self.coh = sequence, coh
        self.unpairs, self.pairs, self.copairs = set(sequence), {}, {}
    def __iter__(self):
        yield from (reversed(self.sequence) if self.coh else self.sequence)
    def __setitem__(self, b, d):
        if self.coh:
            b, d = d, b
        self.pairs[b] = d
        self.copairs[d] = b
        self.unpairs.remove(b)
        self.unpairs.remove(d)
    def _paired(self, low):
        return low is not None and low in (self.copairs if self.coh else self.pairs)
    def _pair(self, low):
        pairs = self.copairs if self.coh else self.pairs
        return pairs[low] if low in pairs else None
    def _reduce(self, D, R, i):
        low = D[i].get_pivot(R)
        while self._paired(low):
            D[i] += D[self._pair(low)]
            low = D[i].get_pivot(R)
        if low is not None:
            self[low] = i
    def _phcol_reduce(self, F, R=set(), verbose=False):
        it = tqdm(self, total=len(self.sequence), desc='[ persist') if verbose else self
        D = F.get_matrix(self, self.coh)
        for i in it:
            self._reduce(D, R, i)
        return D
    def _clearing_reduce(self, F, R=set(), verbose=False):
        D = F.get_matrix(self, self.coh)
        dit = list(range(F.dim+1) if self.coh else reversed(range(F.dim+1)))
        dseq = {dim : [] for dim in dit}
        for i in self:
            dseq[F[i].dim].append(i)
        if verbose:
            pbar = tqdm(total=len(self.sequence), desc='[ persist')
        for dim in dit:
            for i in dseq[dim]:
                if not self._paired(i):
                    self._reduce(D, R, i)
                if verbose:
                    pbar.update(1)
        if verbose:
            pbar.close()
        return D
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
    def get_diagram(self, F):
        dgms = [np.ndarray((0,2), dtype=float) for d in range(F.dim+1)]
        for i,j in self.items():
            p = np.array([F[i].data[F.key], F[self[i]].data[F.key]])
            if F.reverse:
                p = p[::-1]
            if p[0] < p[1]:
                dgms[F[i].dim] = np.vstack((dgms[F[i].dim], p))
        for i in self.unpairs:
            p = np.array([F[i].data[F.key], np.inf])
            dgms[F[i].dim] = np.vstack((dgms[F[i].dim], p))
        return dgms

class Diagram(DiagramBase):
    def __init__(self, F, R=set(), coh=False, clearing=False, verbose=False):
        self.F, self.R = F, R
        DiagramBase.__init__(self, F.get_range(R), coh)
        self.D = (self._clearing_reduce if clearing else self._phcol_reduce)(F, R, verbose)
    def __contains__(self, i):
        if not isinstance(i, int):
            i = self.F[i]
        return DiagramBase.__contains__(self, i)
    def __call__(self, i):
        if not isinstance(i, int):
            i = self.F.index(i)
        if i in self.pairs:
            p = np.array([self.F(i), self.F(self[i])])
            return p[::-1] if self.F.reverse else p
        return np.array([self.F(i), np.inf])
    def is_relative(self, i):
        if not isinstance(i, int):
            i = self.F.index(i)
        return i in self.R
    def persistence(self, i):
        return diff(self(i))
    def get_diagram(self):
        return DiagramBase.get_diagram(self, self.F)
