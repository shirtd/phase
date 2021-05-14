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
        self.elements[key] = element
        self.actors[key] = self.figure.add_mesh(element, **kwargs)
        return self.elements[key]
    def remove(self, key=None):
        if key is None:
            keys = [k for k in self.actors]
            for key in keys:
                self.remove(key)
        else:
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
    def get_simplex(self, i):
        return self.data.current_dgm.F[i]
    def get_cycle(self, i):
        C = self.data.current_dgm.D[i].simplices
        if self.get_simplex(i).dim > 0:
            return [list(s) for s in C]
        return [v for s in C for v in s]
    def get_boundary(self, i):
        C = self.data.current_dgm.D[i].boundary
        if self.get_simplex(i).dim > 1:
            return [list(self.get_simplex(l)) for l in C]
        elif self.get_simplex(i).dim > 0:
            return [v for l in C for v in self.get_simplex(l)]
        return []
    def get_points(self, idx=None):
        P = self.data.input_data[self.data.current_frame]
        if idx is None:
            return P
        return P[idx]
    def __getitem__(self, i):
        return self.data.current_dgm.pairs[i]
    def plot_vertices(self, V, key, *args, **kwargs):
        self.plot_points(self.get_points(V), 0.1, *args, **kwargs)
    def plot_edges(self, V, key, *args, **kwargs):
        self.plot_points(self.get_points(V), 0.1, *args, **kwargs)
    def plot_cycle(self, i, key, **kwargs):
        P, s, c =  self.get_points(), self.get_simplex(i), self.get_cycle(i)
        if s.dim == 0:
            return self.plot_points(P[c], key, 0.1, **kwargs)
        elif s.dim == 1:
            return self.plot_curves(P, c, key, **kwargs)
        elif s.dim == 2:
            return self.plot_faces(P, c, key, opacity=0.5, **kwargs)
        elif s.dim == 3:
            return self.plot_polys(P, c, key, **kwargs)
    def plot_rep(self, i):
        j = self.data.current_dgm[i]
        P = self.data.input_data[self.data.current_frame]
        self.plot_points(self.get_points(), 'points', 0.03)
        self.plot_cycle(i, 'birth', color='green')
        self.plot_cycle(self[i], 'death', color='red')
