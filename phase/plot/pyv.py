from phase.util import stuple

import pyvistaqt as pvqt
import pyvista

from itertools import combinations
import numpy as np


DEFAULT = {'point' : {'radius' : 0.04, 'color' : 'white'},
            'line' : {'radius' : 0.02, 'color' : 'white', 'smooth_shading' : True},
            'surface' : {'color' : '#1E88E5', 'opacity' : 0.7},
            'solid' : {'color' : '#1E88E5', 'opacity' : 1}}


class PYVPlot:
    def __init__(self, bounds=(0,8)):
        self.figure = None
        self.elements = {}
        self.actors = {}
        self.bounds = bounds
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
        # element.clip_box(self.clip)
        self.actors[key] = self.figure.add_mesh(element, **kwargs)
        self.elements[key] = element
        return self.elements[key]
    def remove(self, key=None, keep=set()):
        if key is None:
            keys = [k for k in self.actors]
            for key in keys:
                if not key in keep:
                    self.remove(key)
        elif key in self.elements:
            self.figure.remove_actor(self.actors[key])
            del self.elements[key]
            del self.actors[key]
    def plot_points(self, points, key, radius=DEFAULT['point']['radius'], **kwargs):
        points = np.array([p for p in points if all(self.bounds[0] <= c <= self.bounds[1] for c in p)])
        element = pyvista.PolyData(points).glyph(scale=False, geom=pyvista.Sphere(radius=radius))
        kwargs = {**{'color' : DEFAULT['point']['color']}, **kwargs}
        return self.add_element(element, key, **kwargs)
    def plot_faces(self, points, faces, key, **kwargs):
        element = pyvista.PolyData(points, np.hstack([[len(f)] + list(f) for f in faces]))
        kwargs = {**DEFAULT['surface'], **kwargs}
        return self.add_element(element, key, **kwargs)
    def plot_polys(self, points, polys, key, **kwargs):
        faces = polys # list(map(list,{stuple(t) for p in polys for t in combinations(p, 3)}))
        kwargs = {**DEFAULT['solid'], **kwargs}
        return self.plot_faces(points, faces, key, **kwargs)
    def plot_curve(self, points, path, key, radius=DEFAULT['line']['radius'], **kwargs):
        element = pyvista.PolyData(points, lines=np.array([len(path)] + path))
        if radius is not None:
            element = element.tube(radius=radius)
        kwargs = {**{'color' : DEFAULT['line']['color']}, **kwargs}
        return self.add_element(element, key, **kwargs)
    def plot_curves(self, points, curves, key, radius=DEFAULT['line']['radius'], **kwargs):
        element = pyvista.PolyData(points, lines=np.hstack([[len(c)] + c for c in curves]))#.tube(radius=radius)
        if radius is not None:
            element = element.tube(radius=radius)
        kwargs = {**{'color' : DEFAULT['line']['color']}, **kwargs}
        return self.add_element(element, key, **kwargs)

class ChainPlot(PYVPlot):
    def __init__(self, data):
        PYVPlot.__init__(self)
        self.data = data
        self.dgm = None
    def __getitem__(self, i):
        return self.dgm.pairs[i]
    def get_simplex(self, i):
        return self.dgm.F[i]
    def get_index(self, s):
        return self.dgm.F.index(s)
    def get_points(self, idx=None):
        if idx is None:
            return self.dgm.F.K.P
        return self.dgm.F.K.P[idx]
    # def get_cycle(self, i):
    #     return self.format_cycle(self.dgm.D[i].simplices, self.get_simplex(i).dim)
    # def get_boundary(self, i):
    #     C = [self.get_simplex(l) for l in self.dgm.D[i].boundary]
    #     return self.format_cycle(C, self.get_simplex(i).dim-1)
    # def plot_cycle(self, i, key, **kwargs):
    #     return self.plot_chain(self.get_points(), self.get_cycle(i), self.get_simplex(i).dim, key, **kwargs)
    def format_cycle(self, C, dim, K=None):
        K = self.dgm.F.K if K is None else K
        return ([v for s in C for v in s] if dim == 0
            else [list(s) for s in C if len(s) == 2] if dim == 1
            else [K.orient_face(s) for s in C] if dim == 2
            else list(map(K.orient_face, {f for t in C for f in t.faces})) if dim == 3
            else [])
    def plot_chain(self, c, dim, key, K=None, P=None, **kwargs):
        K = self.dgm.F.K if K is None else K
        c = self.format_cycle(c, dim, K)
        P = K.P if P is None else P
        return (self.plot_points(P[c], key, **kwargs) if dim == 0
            else self.plot_curves(P, c, key, **kwargs) if dim == 1
            else self.plot_faces(P, c, key, **kwargs) if dim == 2
            else self.plot_polys(P, c, key, **kwargs) if dim == 3
            else None)
