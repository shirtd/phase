from phase.util import stuple

import pyvistaqt as pvqt
import pyvista

from itertools import combinations
import numpy as np

class PYVPlot:
    def __init__(self):
        self.figure = None
        self.elements = {}
        self.actors = {}
    def clear_fig(self, close=False):
        if close:
            if self.figure is not None:
                self.figure.close()
            return self.init_fig()
        if self.figure is None:
            return self.init_fig()
        self.figure.clear()
        return self.figure
    def init_fig(self):
        self.figure = pvqt.BackgroundPlotter()
        return self.figure
    def add_element(self, element, key, **kwargs):
        if self.figure is None:
            self.init_fig()
        if key in self.elements:
            self.remove(key)
        self.actors[key] = self.figure.add_mesh(element, **kwargs)
        self.elements[key] = element
        return self.elements[key]
    def remove(self, key=None):
        if key is None:
            keys = [k for k in self.actors]
            for key in keys:
                self.remove(key)
        elif key in self.elements:
            self.figure.remove_actor(self.actors[key])
            del self.elements[key]
            del self.actors[key]
    def plot_points(self, points, key, radius=0.1, **kwargs):
        element = pyvista.PolyData(points).glyph(scale=False, geom=pyvista.Sphere(radius=radius))
        return self.add_element(element, key, **kwargs)
    def plot_faces(self, points, faces, key, **kwargs):
        element = pyvista.PolyData(points, np.hstack([[len(f)] + list(f) for f in faces]))
        return self.add_element(element, key, **kwargs)
    def plot_polys(self, points, polys, key, **kwargs):
        faces = list(map(list,{stuple(t) for p in polys for t in combinations(p, 3)}))
        return self.plot_faces(points, faces, key, **kwargs)
    def plot_curve(self, points, path, key, radius=0.05, **kwargs):
        element = pyvista.PolyData(points, lines=np.array([len(path)] + path))#.tube(radius=radius)
        return self.add_element(element, key, **kwargs)
    def plot_curves(self, points, curves, key, radius=0.05, **kwargs):
        element = pyvista.PolyData(points, lines=np.hstack([[len(c)] + c for c in curves]))#.tube(radius=radius)
        return self.add_element(element, key, **kwargs)

class ChainPlot(PYVPlot):
    def __init__(self, data):
        PYVPlot.__init__(self)
        self.data = data
        self.current_dgm = None
    def get_simplex(self, i):
        return self.current_dgm.F[i]
    def format_cycle(self, C, dim, K=None):
        K = self.current_dgm.F.complex if K is None else K
        if dim == 0:
            return [v for s in C for v in s]
        elif dim == 1:
            return [list(s) for s in C if len(s) == 2]
        elif dim == 2:
            return [K.orient_face(s) for s in C]
        elif dim == 3:
            return list(map(K.orient_face, {f for t in C for f in t.faces}))
        return []
    def get_cycle(self, i):
        return self.format_cycle(self.current_dgm.D[i].simplices, self.get_simplex(i).dim)
    def get_boundary(self, i):
        C = [self.get_simplex(l) for l in self.current_dgm.D[i].boundary]
        return self.format_cycle(C, self.get_simplex(i).dim-1)
    # def get_cycle(self, i):
    #     C = self.current_dgm.D[i].simplices
    #     if self.get_simplex(i).dim > 0:
    #         return [list(s) for s in C]
    #     return [v for s in C for v in s]
    # def get_boundary(self, i):
    #     C = self.current_dgm.D[i].boundary
    #     if self.get_simplex(i).dim > 1:
    #         return [list(self.get_simplex(l)) for l in C]
    #     elif self.get_simplex(i).dim > 0:
    #         return [v for l in C for v in self.get_simplex(l)]
    #     return []
    def get_points(self, idx=None):
        if idx is None:
            return self.current_dgm.F.complex.P
        return self.current_dgm.F.complex.P[idx]
    def __getitem__(self, i):
        return self.current_dgm.pairs[i]
    def plot_vertices(self, V, key, *args, **kwargs):
        self.plot_points(self.get_points(V), 0.1, *args, **kwargs)
    def plot_edges(self, V, key, *args, **kwargs):
        self.plot_points(self.get_points(V), 0.1, *args, **kwargs)
    def plot_cycle(self, i, key, **kwargs):
        return self.plot_chain(self.get_points(), self.get_cycle(i), self.get_simplex(i).dim, key, **kwargs)
    def plot_chain(self, P, c, dim, key, **kwargs):
        if dim == 0:
            return self.plot_points(P[c], key, 0.1, **kwargs)
        elif dim == 1:
            return self.plot_curves(P, c, key, **kwargs)
        elif dim == 2:
            return self.plot_faces(P, c, key, opacity=0.5, **kwargs)
        elif dim == 3:
            return self.plot_faces(P, c, key, **kwargs)
    # def plot_dual(self, i, key, **kwargs):
    #     s = self.get_simplex(i)
    #     if s.dim < 2:
    #         return
    #     V, E, F, C = self.data.dual()
    # def plot_rep(self, i):
    #     j = self.data.current_dgm[i]
    #     P = self.data.input_data[self.data.current_frame]
    #     # R = self.data.current_dgm.R
    #     # if not 'boundary' in self.elements and R:
    #     #     bdy = []
    #     #     for j in R:
    #     #         s = self.get_simplex(j)
    #     #         if s.dim == 2:
    #     #             bdy.append(list(s))
    #     #     self.plot_faces(P, bdy, 'boundary', color='white', opacity=0.01)
    #     self.plot_points(self.get_points(), 'points', 0.03)
    #     self.plot_cycle(i, 'birth', color='green')
    #     self.plot_cycle(self[i], 'death', color='red')
