import numpy as np

def get_lim(dgms):
    return max(d if d < np.inf else b for dgm in dgms for b,d in dgm)

def fill_cochain(dgm, birth):
    C = None
    L = sorted(dgm.D[birth], key=lambda s: dgm.F.index(s))
    for l in L:
        i = dgm.F.index(l)
        if i in dgm.pairs:
            c = dgm.D[dgm.pairs[i]]
            C = c if C is None else C + c
    return C

def fill_chain(dgm, birth, C=None):
    if dgm.coh:
        return fill_cochain(dgm, birth)
    C = dgm.D[dgm.pairs[birth]] if C is None else C
    diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + dgm.D[birth] if not dgm.F.index(s) in dgm.R]
    if len(diff):
        p = max(diff)
        if p in dgm.pairs:
            return fill_chain(dgm, birth, C + dgm.D[dgm.pairs[p]])
    return C
