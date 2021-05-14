from phase.base import PersistenceData
from phase.data import BOUNDS
from phase.simplicial import DioComplex, Filtration
from phase.persist import phcol
from phase.plot.pyv import PYVPlot
from phase.plot.mpl import PersistencePlot
from phase.plot.interact import Interact

from ripser import ripser
import numpy.linalg as la
import dionysus as dio
import numpy as np
import diode


class RipsPersistence(PersistenceData):
    args = ['dim', 'thresh']
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'Rips'
    @classmethod
    def get_name(cls, input_data, *args, **kwargs):
        return '%s_rips' % input_data.name
    @classmethod
    def get_title(cls, input_data, *args, **kwargs):
        return '%s rips' % input_data.title
    def __init__(self, input_data, dim, thresh):
        name = self.get_name(input_data)
        title = self.get_title(input_data)
        prefix = self.get_prefix()
        data = self.run(input_data, prefix, dim, thresh)
        PersistenceData.__init__(self, input_data, data, name, title, prefix, dim)
    def __call__(self, d, dim, thresh):
        return ripser(d, dim, thresh)['dgms']

def format_float(f):
    if f.is_integer():
        return int(f)
    e = 0
    while not f.is_integer():
        f *= 10
        e -= 1
    return '%de%d' % (int(f), e)

class AlphaPersistence(PersistenceData):
    args = ['dim', 'delta']
    @classmethod
    def get_prefix(cls, delta, *args, **kwargs):
        prefix = 'Alpha'
        if delta > 0:
            prefix = '%s (delta=%g)' % (prefix, delta)
        return prefix
    @classmethod
    def get_name(cls, input_data, delta, *args, **kwargs):
        name = '%s_alpha' % input_data.name
        if delta > 0:
            name = '%s-delta%s' % (name, format_float(delta))
        return name
    @classmethod
    def get_title(cls, input_data, delta, *args, **kwargs):
        title = '%s alpha' % input_data.title
        if delta > 0:
            title = '%s (delta=%g)' % (title, delta)
        return title
    def __init__(self, input_data, dim, delta):
        name = self.get_name(input_data, delta)
        title = self.get_title(input_data, delta)
        prefix = self.get_prefix(delta)
        self.delta, self.bounds = delta, (BOUNDS[0]+delta, BOUNDS[1]-delta)
        dim = input_data.data.shape[-1]
        self.chain_data = self.run(input_data, prefix, dim)
        data = [d.get_diagram() for d in self.chain_data]
        # self.current_frame, self.current_dgm = None, None
        self.current_dgm = None
        PersistenceData.__init__(self, input_data, data, name, title, prefix, dim)
    def is_boundary(self, p):
        return not all(self.bounds[0] < c < self.bounds[1] for c in p)
    def get_boundary(self, P, F):
        if self.delta > 0:
            Q = {i for i,p in enumerate(P) if self.is_boundary(p)}
            return {i for i,s in enumerate(F) if all(v in Q for v in s)}
        return set()
    def __call__(self, P, dim):
        P.dtype = float
        Fdio = dio.Filtration(diode.fill_alpha_shapes(P))
        K = DioComplex(Fdio, 'alpha', dim)
        F = Filtration(K, 'alpha')
        R = self.get_boundary(P, F)
        return phcol(F, R)
    def plot(self, frame, *args, **kwargs):
        res = PersistenceData.plot(self, frame, *args, **kwargs)
        self.current_dgm = self.chain_data[frame]
        return res

class AlphaPersistenceInteract(Interact):
    def __init__(self, data):# *args, **kwargs):
        # AlphaPersistence.__init__(self, *args, **kwargs)
        Interact.__init__(self, data)
        # Interact.__init__(self)
        self.pv = PYVPlot()
        self.data.init_fig()
        self.connect()
    def plot(self, frame, *args, **kwargs):
        return self.data.plot(frame, *args, **kwargs)
    def plot_frame(self, i):
        self.last_frame = i
        # print(self.current_dgm.get_pair(s))
        self.plot_current(i)
        self.plot_rep(i)
        # self.input_data.plot_(frame, self.lim)
        # self.plot_current(frame)
        # plt.show(block=False)
    def plot_rep(self, i):
        j = self.data.current_dgm[i]
        P = self.data.input_data[self.data.current_frame]
        if not 'points' in self.pv.elements:
            self.pv.plot_points(P, 'points', 0.03)#, opacity=0.5)
        if 'birth' in self.pv.elements:
            self.pv.remove('birth')
        if 'death' in self.pv.elements:
            self.pv.remove('death')
        if self.data.current_dgm.F[i].dim == 0:
            E = [list(e) for e in self.data.current_dgm.D[j].simplices]
            self.pv.plot_curves(P, E, 'death', color='red')
            I = [v for s in self.data.current_dgm.D[i].simplices for v in s]
            self.pv.plot_points(P[I], 'birth', 0.1, color='green')
        elif self.data.current_dgm.F[i].dim == 1:
            T = [list(t) for t in self.data.current_dgm.D[j].simplices]
            self.pv.plot_faces(P, T, 'death', color='red', opacity=0.5)
            E = [list(e) for e in self.data.current_dgm.D[i].simplices]
            self.pv.plot_curves(P, E, 'birth', color='green')
        elif self.data.current_dgm.F[i].dim == 2:
            L = [list(self.data.current_dgm.F[l]) for l in self.data.current_dgm.D[j].boundary] # simplices]
            self.pv.plot_polys(P, L, 'death', color='red')# , opacity=0.7)
            T = [list(t) for t in self.data.current_dgm.D[i].simplices]
            self.pv.plot_faces(P, T, 'birth', color='green', opacity=0.5)#, opacity=0.5)
    def get_closest(self, event):
        p = np.array([event.xdata, event.ydata])
        dst = lambda s: la.norm(p - self.data.current_dgm.get_pair(s))
        return min([b for b in self.data.current_dgm.pairs], key=dst)
    # def prompt(self):
    #     return '[ Plot frame (0-%d): ' % len(self)
    def plot_current(self, i):
        while self.cur_frame_plt:
            self.cur_frame_plt.pop().remove()
        s = self.data.current_dgm.F[i]
        p = self.data.current_dgm.get_pair(i)
        self.cur_frame_plt.append(self.data.axis.scatter(p[0], p[1], s=50, color=self.data.COLORS[s.dim], zorder=2))
        self.data.update_figure()

# class AlphaPersistenceInteract(AlphaPersistence, Interact):
#     def __init__(self, *args, **kwargs):
#         AlphaPersistence.__init__(self, *args, **kwargs)
#         self.current_dgm = None
#         Interact.__init__(self)
#         self.pv = PYVPlot()
#     def init_fig(self):
#         res = PersistencePlot.init_fig(self)
#         self.connect()
#         return res
#     def plot(self, frame, *args, **kwargs):
#         self.current_frame = frame
#         self.current_dgm = self.chain_data[frame]
#         self.pv.remove()
#         return PersistencePlot.plot(self, frame, *args, **kwargs)
#     def plot_frame(self, i):
#         self.last_frame = i
#         # print(self.current_dgm.get_pair(s))
#         self.plot_current(i)
#         self.plot_rep(i)
#         # self.input_data.plot_(frame, self.lim)
#         # self.plot_current(frame)
#         # plt.show(block=False)
    # def plot_rep(self, i):
    #     j = self.current_dgm[i]
    #     P = self.input_data[self.current_frame]
    #     if not 'points' in self.pv.elements:
    #         self.pv.plot_points(P, 'points', 0.03)#, opacity=0.5)
    #     if 'birth' in self.pv.elements:
    #         self.pv.remove('birth')
    #     if 'death' in self.pv.elements:
    #         self.pv.remove('death')
    #     if self.current_dgm.F[i].dim == 0:
    #         E = [list(e) for e in self.current_dgm.D[j].simplices]
    #         self.pv.plot_curves(P, E, 'death', color='red')
    #         I = [v for s in self.current_dgm.D[i].simplices for v in s]
    #         self.pv.plot_points(P[I], 'birth', 0.1, color='green')
    #     elif self.current_dgm.F[i].dim == 1:
    #         T = [list(t) for t in self.current_dgm.D[j].simplices]
    #         self.pv.plot_faces(P, T, 'death', color='red', opacity=0.5)
    #         E = [list(e) for e in self.current_dgm.D[i].simplices]
    #         self.pv.plot_curves(P, E, 'birth', color='green')
    #     elif self.current_dgm.F[i].dim == 2:
    #         L = [list(self.current_dgm.F[l]) for l in self.current_dgm.D[j].boundary] # simplices]
    #         self.pv.plot_polys(P, L, 'death', color='red')# , opacity=0.7)
    #         T = [list(t) for t in self.current_dgm.D[i].simplices]
    #         self.pv.plot_faces(P, T, 'birth', color='green', opacity=0.5)#, opacity=0.5)
#     def get_closest(self, event):
#         p = np.array([event.xdata, event.ydata])
#         dst = lambda s: la.norm(p - self.current_dgm.get_pair(s))
#         return min([b for b in self.current_dgm.pairs], key=dst)
#     # def prompt(self):
#     #     return '[ Plot frame (0-%d): ' % len(self)
#     def plot_current(self, i):
#         while self.cur_frame_plt:
#             self.cur_frame_plt.pop().remove()
#         s = self.current_dgm.F[i]
#         p = self.current_dgm.get_pair(i)
#         self.cur_frame_plt.append(self.axis.scatter(p[0], p[1], s=50, color=self.COLORS[s.dim], zorder=2))
#         self.update_figure()
