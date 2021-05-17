from phase.plot.mpl import MPLPlot, plt
from phase.plot.pyv import ChainPlot
from phase.stats import PersHisto

from phase.topology.util import fill_chain
from phase.topology.cells import DualComplex

import numpy.linalg as la
import numpy as np
import time
import sys

class Interact: # (MPLPlot):
    def __init__(self, data):
        self.data = data
        self.cids, self.cur_frame_plt = {}, []
        self.last_frame, self.press_time = -1, None
        # self.run()
    def connect(self):
        self.cids['button_press_event'] = self.data.figure.canvas.mpl_connect('button_press_event', self.onclick)
        self.cids['button_release_event'] = self.data.figure.canvas.mpl_connect('button_release_event', self.onrelease)
        self.cids['key_press_event'] = self.data.figure.canvas.mpl_connect('key_press_event', self.onpress)
    def disconnect(self):
        for k in self.cids:
            self.data.figure.canvas.mpl_disconnect(self.cids[k])
            del self.cids[k]
    def run(self):
        input('[ Exit ]')
    def onclick(self, event):
        self.press_time = time.time()
    def onrelease(self, event):
        if self.is_event(event):
            frame = self.get_closest(event)
            self.plot_frame(frame)
            self.data.raise_figure()
    def onpress(self, event):
        if event.key == 'right':
            frame = self.get_next()
        elif event.key == 'left':
            frame = self.get_prev()
        else:
            return
        self.plot_frame(frame)
        self.data.raise_figure()
    def is_event(self, event):
        if self.press_time is None or time.time() - self.press_time > 0.5:
            return False
        try:
            iter(self.data.axis)
        except TypeError:
            return event.inaxes == self.data.axis
        return any(event.inaxes == ax for ax in self.data.axis)
    def plot_frame(self, frame):
        pass
    def get_closest(self, event):
        pass
    def plot_next(self):
        pass
    def plot_prev(self):
        pass

class TPersInteract(Interact):
    def __init__(self, data, sub=None, value='tpers'):
        Interact.__init__(self, data)
        self.histo = PersHisto(data, value)
        self.sub = sub
        self.data.plot()
        plt.show(block=False)
        self.connect()
        self.run()
    def plot_frame(self, frame):
        if frame < len(self.data):
            self.last_frame = frame
            if self.sub is None:
                self.data.input_data.plot(frame, self.data.lim)
            else:
                self.sub.plot(frame, self.data.lim, self.data)
                # self.histo(frame, self.sub.active_dgm)
            self.histo(frame, self.data.input_data[frame])
            self.plot_current(frame)
            plt.show(block=False)
        else:
            print(' ! Invalid frame')
    def get_closest(self, event):
        return min(max(int(np.round(event.xdata)),0), len(self.data)-1)
    def plot_current(self, frame):
        while self.cur_frame_plt:
            self.cur_frame_plt.pop().remove()
        for d, ax in enumerate(self.data.axis[1:]):
            kwargs = {'color' : self.data.COLORS[d], 's' : 50, 'zorder' : 2}
            self.cur_frame_plt.append(ax.scatter([frame], [self.data[frame,d]], **kwargs))
            self.cur_frame_plt.append(self.data.axis[0].scatter([frame], [self.data[frame,d]], **kwargs))
        self.data.update_figure()
    def get_next(self):
        return (self.last_frame+1) % len(self.data)
    def get_prev(self):
        return (self.last_frame-1) % len(self.data)

class MyPersistenceInteract(Interact, ChainPlot):
    def __init__(self, data):
        Interact.__init__(self, data)
        ChainPlot.__init__(self, data)
        self.active_pairs = {}
        self.sorted_births = []
        self.data.init_fig()
        self.connect()
        self.dualized = False
        self.filled = False
        self.current_dual = None
    def onpress(self, event):
        if event.key == 'd':
            self.plot_dual()
        # if event.key == 'e':
        #     self.plot_dual(True)
        if event.key == 'c':
            self.fill_cycle()
        Interact.onpress(self, event)
    def plot(self, frame, lim, tpers_data):
        self.current_dual = None
        self.current_dgm = self.data.chain_data[frame]
        self.active_dgms = [tpers_data.get_range(dgm) for dgm in self.data[frame]]
        self.active_pairs = {b : d for b,d in self.current_dgm.items() if tpers_data.inrng(self.current_dgm(b))}
        self.sorted_births = sorted(self.active_pairs, key=lambda b: self.current_dgm.persistence(b), reverse=True)
        self.birth_imap = {b : i for i,b in enumerate(self.sorted_births)}
        res = self.data.plot(frame, lim, self.active_dgms)
        self.remove()
        self.plot_frame()
        return res
    def plot_frame(self, i=None):
        if i is None and len(self.sorted_births):
            i = self.sorted_births[0]
        elif not len(self.sorted_births):
            return
        self.last_frame = i
        self.plot_current(i)
        self.plot_rep(i)
    def get_closest(self, event):
        if not len(self.active_pairs):
            return None
        p = np.array([event.xdata, event.ydata])
        dst = lambda s: la.norm(p - self.current_dgm(s))
        return min([b for b in self.active_pairs], key=dst)
    def plot_current(self, i):
        while self.cur_frame_plt:
            self.cur_frame_plt.pop().remove()
        s = self.current_dgm.F[i]
        p = self.current_dgm(i)
        self.cur_frame_plt.append(self.data.axis.scatter(p[0], p[1], s=50, color=self.data.COLORS[s.dim], zorder=2))
        self.data.update_figure()
    def get_next(self):
        return self.sorted_births[(self.birth_imap[self.last_frame]+1) % len(self.sorted_births)]
    def get_prev(self):
        return self.sorted_births[(self.birth_imap[self.last_frame]-1) % len(self.sorted_births)]
    def plot_rep(self, i):
        self.remove('dual_death')
        self.remove('dual_birth')
        self.dualized = False
        self.filled = False
        self.plot_points(self.get_points(), 'points', 0.03)
        self.plot_cycle(i, 'birth', color='green')
        self.plot_cycle(self[i], 'death', color='red')
    def fill_cycle(self):
        if self.last_frame is None:
            return
        if self.filled:
            return self.plot_rep(self.last_frame)
        C = fill_chain(self.current_dgm, self.last_frame)
        s = self.get_simplex(self[self.last_frame])
        self.plot_chain(self.get_points(), self.format_cycle(C, s.dim), s.dim, 'death', color='red')
        self.filled = True
    def plot_dual(self, ext=False):
        if self.last_frame is None:
            return
        if self.dualized:
            return self.plot_rep(self.last_frame)
        # self.remove('birth')
        # self.remove('death')
        s = self.get_simplex(self.last_frame)
        dB, dD = self.get_dual(self.last_frame)
        bdim = self.current_dgm.F.dim - s.dim
        ddim, P = bdim - 1, self.current_dual.P
        b = self.format_cycle(dB, bdim, self.current_dual)
        d = self.format_cycle(dD, ddim, self.current_dual)
        self.plot_points(P, 'points', 0.03, color='black')
        self.plot_chain(P, b, bdim, 'birth', color='blue')
        self.plot_chain(P, d, ddim, 'death', color='orange')
        self.dualized = True

class AlphaPersistenceInteract(MyPersistenceInteract):
    def __init__(self, data):
        MyPersistenceInteract.__init__(self, data)
        self.current_dual = None
    def get_dual(self, i):
        K = self.current_dgm.F.complex
        # C = fill_chain(self.current_dgm, i)
        B = self.current_dgm.D[i]
        D = fill_chain(self.current_dgm, i)
        if self.current_dual is None:
            self.current_dual = DualComplex(K, 'alpha')
        birth = [self.current_dual(t) for t in B]
        death = [self.current_dual(t) for t in D]
        return birth, death

class VoronoiPersistenceInteract(MyPersistenceInteract):
    def __init__(self, data):
        MyPersistenceInteract.__init__(self, data)
    def get_dual(self, i):
        K = self.current_dgm.F.complex
        # C = fill_chain(self.current_dgm, i)
        B = self.current_dgm.D[i]
        D = fill_chain(self.current_dgm, i)
        if self.current_dual is None:
            self.current_dual = K.K
        # print(next(iter(fill_chain(self.current_dgm, i))), next(iter(self.current_dgm.D[i])))
        birth = [K.pmap[t] for t in B]
        death = [K.pmap[t] for t in D]
        return birth, death



# class AlphaPersistenceInteract(MyPersistenceInteract):
#     def plot_rep(self, i):
#         if 'dual_death' in self.elements:
#             self.remove('dual_death')
#         if 'dual_birth' in self.elements:
#             self.remove('dual_birth')
#         self.dualized = False
#         self.filled = False
#         self.plot_points(self.get_points(), 'points', 0.03)
#         self.plot_cycle(i, 'birth', color='green')
#         self.plot_cycle(self[i], 'death', color='red')
    # def fill_cycle(self):
    #     if self.last_frame is None:
    #         return
    #     if self.filled:
    #         self.remove('dual_death')
    #         self.remove('dual_birth')
    #         self.plot_cycle(self[self.last_frame], 'death', color='red')
    #         self.filled = False
    #         self.dualized = False
    #     else:
    #         C = [list(s) for s in fill_chain(self.current_dgm, self.last_frame)]
    #         s = self.get_simplex(self[self.last_frame])
    #         self.plot_chain(C, s.dim, 'death', color='red')
    #         self.filled = True
    # def plot_dual(self, ext=False):
    #     if self.last_frame is None:
    #         return
    #     if self.dualized:
    #         self.remove('dual_death')
    #         self.remove('dual_birth')
    #         self.plot_cycle(self[self.last_frame], 'death', color='red')
    #         self.dualized = False
    #         self.filled = False
    #     else:
    #         s = self.get_simplex(self.last_frame)
    #         if s.dim < 2 and not ext:
    #             return
    #         C = fill_chain(self.current_dgm, self.last_frame)
    #         E, F = self.data.dual.tet_chain_dual(C, ext)
    #         self.remove('death')
    #         if len(E):
    #             self.plot_curves(self.data.dual.Q, E, 'dual_death')
    #         if len(F):
    #             self.plot_faces(self.data.dual.Q, F, 'dual_birth', color='blue', opacity=0.3)
    #         self.dualized = True
#
# class VoronoiPeristenceInteract(MyPersistenceInteract):
#     def plot_rep(self, i):
#         if 'dual_death' in self.elements:
#             self.remove('dual_death')
#         if 'dual_birth' in self.elements:
#             self.remove('dual_birth')
#         self.dualized = False
#         self.filled = False
#         self.plot_points(self.get_points(), 'points', 0.03)
#         self.plot_cycle(i, 'birth', color='green')
#         self.plot_cycle(self[i], 'death', color='red')
