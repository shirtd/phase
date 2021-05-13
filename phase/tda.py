from phase.base import PersistenceData
from phase.data import BOUNDS
from phase.simplicial import DioComplex, Filtration
from phase.persist import phcol
from phase.plot.mpl import PersistencePlot

from ripser import ripser
import dionysus as dio
import numpy as np
import diode

# def dio_to_np(D):
#     return [np.array([[p.birth, p.death] for p in dgm]) if len(dgm) else np.ndarray((0,2)) for dgm in D]

class RipsPersistence(PersistenceData, PersistencePlot):
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
        PersistencePlot.__init__(self)
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

class AlphaPersistence(PersistenceData, PersistencePlot):
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
        PersistenceData.__init__(self, input_data, data, name, title, prefix, dim)
        PersistencePlot.__init__(self)
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


# class AlphaPersistenceInteract(AlphaPersistence, Interact):
#     def __init__(self, *args, **kwargs):
#         AlphaPersistence.__init__(self, *args, **kwargs)
#         self.plot(0)
#         plt.show(block=False)
#         Interact.__init__(self)
#     def plot_frame(self, frame):
#         if frame < len(self):
#             self.last_frame = frame
#             self.input_data.plot(frame, self.lim)
#             self.plot_current(frame)
#             plt.show(block=False)
#         else:
#             print(' ! Invalid frame')
#     def get_closest(self, event):
#         return min(max(int(np.round(event.xdata)),0), len(self)-1)
#     def prompt(self):
#         return '[ Plot frame (0-%d): ' % len(self)
#     def plot_current(self, frame):
#         while self.cur_frame_plt:
#             self.cur_frame_plt.pop().remove()
#         for d, ax in enumerate(self.axis[1:]):
#             kwargs = {'color' : self.COLORS[d], 's' : 50, 'zorder' : 2}
#             self.cur_frame_plt.append(ax.scatter([frame], [self.data[frame,d]], **kwargs))
#             self.cur_frame_plt.append(self.axis[0].scatter([frame], [self.data[frame,d]], **kwargs))
#         self.update_figure()
#
# class TPersInteract(TPers, Interact):
#     def __init__(self, input_data, *args, **kwargs):
#         self.input_data = input_data
#         TPers.__init__(self, input_data, *args, **kwargs)
#         self.plot()
#         plt.show(block=False)
#         Interact.__init__(self)
#     def plot_frame(self, frame):
#         if frame < len(self):
#             self.last_frame = frame
#             self.input_data.plot(frame, self.lim)
#             self.plot_current(frame)
#             plt.show(block=False)
#         else:
#             print(' ! Invalid frame')
#     def get_closest(self, event):
#         return min(max(int(np.round(event.xdata)),0), len(self)-1)
#     def prompt(self):
#         return '[ Plot frame (0-%d): ' % len(self)
#     def plot_current(self, frame):
#         while self.cur_frame_plt:
#             self.cur_frame_plt.pop().remove()
#         for d, ax in enumerate(self.axis[1:]):
#             kwargs = {'color' : self.COLORS[d], 's' : 50, 'zorder' : 2}
#             self.cur_frame_plt.append(ax.scatter([frame], [self.data[frame,d]], **kwargs))
#             self.cur_frame_plt.append(self.axis[0].scatter([frame], [self.data[frame,d]], **kwargs))
#         self.update_figure()
