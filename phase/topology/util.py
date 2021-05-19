import numpy as np

def get_lim(dgms):
    return max(d if d < np.inf else b for dgm in dgms for b,d in dgm)

# def fill_cochain(dgm, birth):
#     C = None
#     L = sorted(dgm.D[birth], key=lambda s: dgm.F.index(s))
#     for l in L:
#         i = dgm.F.index(l)
#         if i in dgm.pairs:
#             c = dgm.D[dgm.pairs[i]]
#             C = c if C is None else C + c
#     return C
#
# def fill_chain(dgm, birth, C=None):
#     if dgm.coh:
#         return fill_cochain(dgm, birth)
#     C = dgm.D[dgm.pairs[birth]] if C is None else C
#     diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + dgm.D[birth] if not dgm.F.index(s) in dgm.R]
#     if len(diff):
#         p = max(diff)
#         if p in dgm.pairs:
#             return fill_chain(dgm, birth, C + dgm.D[dgm.pairs[p]])
#     return C

def fill_birth(dgm, birth, pre=False):
    C = None
    if dgm.coh:
        return fill_birth_coh(dgm, birth, C, pre)
    c = fill_death(dgm, birth, C, False) if pre else dgm.D[dgm[birth]]
    L = sorted(c, key=lambda s: dgm.F.index(s))
    for l in L:
        i = dgm.F.index(l)
        if i in dgm.pmap:
            D = dgm.D[dgm.pmap[i]]
            C = D if C is None else C + D
    return C


def fill_birth_coh(dgm, birth, C=None, pre=False, c=None):
    C = dgm.D[birth] if C is None else C # fill_birth(dgm, birth)
    if c is None:
        c = fill_death_coh(dgm, birth, False) if pre else dgm.D[dgm[birth]]
    diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + c if not dgm.F.index(s) in dgm.R]
    # diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + fill_death_coh(dgm, birth) if not dgm.F.index(s) in dgm.R]
    if len(diff):
        p = min(diff)
        if p in dgm.pmap:
            return fill_birth_coh(dgm, birth, C + dgm.D[dgm.pmap[p]], pre, c)
    return C

def fill_death(dgm, birth, C=None, pre=False, c=None):
    if dgm.coh:
        return fill_death_coh(dgm, birth, pre)
    if C is None:
        C = dgm.D[dgm.pairs[birth]]
    if c is None:
        c = fill_birth(dgm, birth, False) if pre else dgm.D[birth]
    diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + c if not dgm.F.index(s) in dgm.R]
    # diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + fill_birth(dgm, birth) if not dgm.F.index(s) in dgm.R]
    if len(diff):
        p = max(diff)
        if p in dgm.pairs:
            return fill_death(dgm, birth, C + dgm.D[dgm.pairs[p]], pre, c)
    return C

def _fill_death(dgm, birth, C=None, pre=False, c=None, added=set()):
    if dgm.coh:
        return _fill_death_coh(dgm, birth, pre)
    if C is None:
        C = dgm.D[dgm.pairs[birth]]
    if c is None:
        c = fill_birth(dgm, birth, False) if pre else dgm.D[birth]
    diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + c if not dgm.F.index(s) in dgm.R]
    # diff = [dgm.F.index(s) for s in dgm.F.boundary(C) + fill_birth(dgm, birth) if not dgm.F.index(s) in dgm.R]
    if len(diff):
        p = max(diff)
        if p in dgm.pairs:
            added.add(p)
            return _fill_death(dgm, birth, C + dgm.D[dgm.pairs[p]], pre, c, added)
    return C, added

def fill_death_coh(dgm, birth, pre=False):
    C = None
    c = fill_birth_coh(dgm, birth, C, False) if pre else dgm.D[birth]
    L = sorted(c, key=lambda s: dgm.F.index(s))
    # L = sorted(dgm.D[birth], key=lambda s: dgm.F.index(s))
    for l in L:
        i = dgm.F.index(l)
        if i in dgm.pairs:
            D = dgm.D[dgm.pairs[i]]
            C = D if C is None else C + D
    return C

def _fill_death_coh(dgm, birth, pre=False, added=set()):
    C = None
    c = fill_birth_coh(dgm, birth, C, False) if pre else dgm.D[birth]
    L = sorted(c, key=lambda s: dgm.F.index(s))
    # L = sorted(dgm.D[birth], key=lambda s: dgm.F.index(s))
    for l in L:
        i = dgm.F.index(l)
        if i in dgm.pairs:
            added.add(i)
            D = dgm.D[dgm.pairs[i]]
            C = D if C is None else C + D
    return C, added
