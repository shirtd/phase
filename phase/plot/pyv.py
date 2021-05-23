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
    def __init__(self, bounds):
        self.figure = None
        self.elements = {}
        self.actors = {}
        self.bounds = bounds
    def __contains__(self, key):
        return key in self.actors
    def __getitem__(self, key):
        return self.actors[key]
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
    def hide(self, key=None, keep=set()):
        if key is None:
            keys = [k for k in self.actors]
            for key in keys:
                if not key in keep:
                    self[key].VisibilityOff()
        elif key in self.elements:
            self[key].VisibilityOff()
    def show(self, key=None, keep=set()):
        if key is None:
            keys = [k for k in self.actors]
            for key in keys:
                if not key in keep:
                    self[key].VisibilityOn()
        elif key in self.elements:
            self[key].VisibilityOn()
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
        points = np.array([p for p in points if all(0 <= c <= l for l,c in zip(self.bounds, p))])
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
    def __init__(self, pers_data, filt_data, input_data, bounds):
        PYVPlot.__init__(self, bounds)
        self.pers_data, self.filt_data, self.input_data = pers_data, filt_data, input_data
        self.last_frame_sup, self.dgm, self.F, self.P = None, None, None, None
    def set_frame(self, frame):
        self.last_frame_sup = frame
        self.dgm = self.pers_data.reps[frame]
        self.F = self.filt_data[frame]
        self.P = self.input_data[frame]
    def format_cycle(self, C, dim, K=None):
        K = self.F.K if K is None else K
        # C = [self.F[i] for i in c]
        return ([v for s in C for v in s] if dim == 0
            else [list(s) for s in C if len(s) == 2] if dim == 1
            else [K.orient_face(s) for s in C] if dim == 2
            else list(map(K.orient_face, {f for t in C for f in t.faces})) if dim == 3
            else [])
    # def format_cycle(self, C, dim, K=None):
    #     K = self.F.K if K is None else K
    #     return ([v for s in C for v in s] if dim == 0
    #         else [list(self.Fs) for s in C if len(s) == 2] if dim == 1
    #         else [K.orient_face(s) for s in C] if dim == 2
    #         else list(map(K.orient_face, {f for t in C for f in t.faces})) if dim == 3
    #         else [])
    def plot_chain(self, c, dim, key, K=None, P=None, **kwargs):
        K = self.F.K if K is None else K
        c = self.format_cycle(c, dim, K)
        P = K.P if P is None else P
        return (self.plot_points(P[c], key, **kwargs) if dim == 0
            else self.plot_curves(P, c, key, **kwargs) if dim == 1
            else self.plot_faces(P, c, key, **kwargs) if dim == 2
            else self.plot_polys(P, c, key, **kwargs) if dim == 3
            else None)

# class ChainPlot(PYVPlot):
#     def __init__(self, data, bounds):
#         PYVPlot.__init__(self, bounds)
#         self.data = data
#         self.dgm = None
#     def __getitem__(self, i):
#         return self.dgm.pairs[i]
#     def get_simplex(self, i):
#         return self.dgm.F[i]
#     def get_index(self, s):
#         return self.dgm.F.index(s)
#     def get_points(self, idx=None):
#         if idx is None:
#             return self.dgm.F.K.P
#         return self.dgm.F.K.P[idx]
#     def format_cycle(self, C, dim, K=None):
#         K = self.dgm.F.K if K is None else K
#         return ([v for s in C for v in s] if dim == 0
#             else [list(s) for s in C if len(s) == 2] if dim == 1
#             else [K.orient_face(s) for s in C] if dim == 2
#             else list(map(K.orient_face, {f for t in C for f in t.faces})) if dim == 3
#             else [])
#     def plot_chain(self, c, dim, key, K=None, P=None, **kwargs):
#         K = self.dgm.F.K if K is None else K
#         c = self.format_cycle(c, dim, K)
#         P = K.P if P is None else P
#         return (self.plot_points(P[c], key, **kwargs) if dim == 0
#             else self.plot_curves(P, c, key, **kwargs) if dim == 1
#             else self.plot_faces(P, c, key, **kwargs) if dim == 2
#             else self.plot_polys(P, c, key, **kwargs) if dim == 3
#             else None)
