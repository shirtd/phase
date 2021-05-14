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

#
# def polyline_from_points(points):
#     poly = pv.PolyData()
#     poly.points = points
#     the_cell = np.arange(0, len(points), dtype=np.int_)
#     the_cell = np.insert(the_cell, 0, len(points))
#     poly.lines = the_cell
#     return poly
#
# polyline = polyline_from_points(points)
# polyline["scalars"] = np.arange(polyline.n_points)
# tube = polyline.tube(radius=0.1)
# tube.plot(smooth_shading=True)
    # def update_figure(self):
    #     self.figure.canvas.draw()
    #     self.figure.canvas.flush_events()
    # def raise_figure(self):
    #     self.figure.canvas.manager.window.activateWindow()
    #     self.figure.canvas.manager.window.raise_()
    # def get_limits(self, mn, mx):
    #     return mx - 1.05*(mx - mn), 1.05*mx
    # def scale_axis(self, axis, xmin, xmax, ymin, ymax):
    #     axis.autoscale(False)
    #     if xmax > xmin:
    #         axis.set_xlim(*self.get_limits(xmin, xmax))
    #     if ymax > ymin:
    #         axis.set_ylim(*self.get_limits(ymin, ymax))

# class PointCloudPlot(PYVPlot):
#     def __init__(self, )
