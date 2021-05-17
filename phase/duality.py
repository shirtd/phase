from phase.topology.simplicial import Simplex
from phase.topology.chains import BoundaryColumn
from phase.topology.util import fill_cochain, fill_chain
from phase.geometry import tet_circumcenter
from phase.util import to_path

import numpy as np

class VoronoiDual:
    def __init__(self, P, F, R):
        self.P, self.F, self.R = P, F, R
        self.tets = sorted(F.complex[3], key=lambda t: t.data['alpha'])
        self.imap = {t : i for i,t in enumerate(self.tets)}
        self.Q = np.vstack([tet_circumcenter(P[list(t)]) for t in self.tets])
        self.emap = {f : [self.imap[t] for t in f.cofaces] for f in F.complex[2] if len(f.cofaces) == 2}# if not F.index(f) in R}
        self.nbrs = {i : set() for i,_ in enumerate(self.tets)}
        for u,v in self.emap.values():
            self.nbrs[u].add(v)
            self.nbrs[v].add(u)
        self.fmap = {e : to_path({v for f in e.cofaces for v in self.emap[f]}, self.nbrs) for e in F.complex[1] if all(f in self.emap for f in e.cofaces)}# if not F.index(e) in R}
        self.cmap = {v : [self.fmap[e] for e in v.cofaces] for v in F.complex[0] if all(e in self.fmap for e in v.cofaces)}# if not F.index(v) in R}
        self.dmap = {**self.emap, **self.fmap, **self.cmap, **self.imap}
    def __call__(self, s):
        if isinstance(s, int):
            s = (s,)
        return self.dmap[s]
    def __contains__(self, s):
        if isinstance(s, int):
            s = (s,)
        return s in self.dmap
    def tet_chain_dual(self, C, ext=False):
        if ext:
            return self.tet_chain_dual_ext(C)
        V = {self(s) for s in C}
        faces = {f for s in C for f in s.faces}
        edges = {e for f in faces for e in self.F.complex(f).faces}
        # vertices = {v for e in edges for v in e}
        dual_edges = [self(f) for f in faces if f in self and all(v in V for v in self(f))]
        dual_faces = [self(e) for e in edges if e in self and all(v in V for v in self(e))]
        return dual_edges, dual_faces
    def tet_chain_dual_ext(self, C):
        vertices = {v for s in C for v in s if not v in self.R}
        dual_cells = [self(v) for v in vertices if v in self]
        return [], list(map(list,{tuple(f) for c in dual_cells for f in c}))
