from phase.base import *
from phase.plot.mpl import TimeSeriesPlot
from phase.plot.interact import Interact

import matplotlib.pyplot as plt
import numpy as np
import time
import sys

# def get_tpers(D, average=False, pmin=0, pmax=np.inf, count=False, bmin=-np.inf):
#     ps = [[d - b for b,d in dgm if pmin <= d - b < pmax and bmin <= b] for dgm in D]
#     if count:
#         return [len(p) for p in ps]
#     elif average:
#         return [sum(p) / len(p) if len(p) else 0 for p in ps]
#     return [sum(p) for p in ps]
#
#     def pers_curve(Ds, average=False, pmin=0, pmax=np.inf, count=False, bmin=-np.inf):
#         return np.vstack([get_tpers(D, average, pmin, pmax, count, bmin) for D in Ds])

class TPers(Data, TimeSeriesPlot):
    module = 'analyze'
    args = ['dim', 'pmin', 'pmax', 'average', 'count', 'lim']
    @classmethod
    def get_prefix(cls, *args, **kwargs):
        return 'TPers'
    @classmethod
    def get_name(cls, input_data, *args, **kwargs):
        return '%s_tpers' % input_data.name
    @classmethod
    def get_title(cls, input_data, *args, **kwargs):
        return '%s TPers' % input_data.title
    def __init__(self, input_data, dim, pmin, pmax, average, count, lim):
        name = self.get_name(input_data)
        title = self.get_title(input_data)
        prefix = self.get_prefix()
        self.dim, self.pmin, self.pmax = dim, pmin, pmax
        self.average, self.count, self.lim = average, count, lim
        data = np.vstack([self(dgms, dim, pmin, pmax, average, count) for dgms in input_data])
        Data.__init__(self, data, name, title, prefix, input_data.features[:dim+1])
        TimeSeriesPlot.__init__(self, len(self.features)+1, 1, sharex=True, figsize=(12,8))
    def __call__(self, dgms, dim, pmin, pmax, average, count):
        ps = [[d - b for b,d in dgm if pmin <= d - b < pmax] for dgm in dgms[:dim+1]]
        if count:
            return [len(p) for p in ps]
        elif average:
            return [sum(p) / len(p) if len(p) else 0 for p in ps]
        return [sum(p) for p in ps]
    # def plot(self, figsize=(12,8), plot_legend=True, make_title=True):
    #     if self.figure is not None or self.axis is not None:
    #         plt.close(self.figure)
    #     self.figure, self.axis = plt.subplots(len(self.features)+1,1, sharex=True, figsize=figsize)
    #     for i, (d, v) in enumerate(zip(self.data.T, self.features)):
    #         self.axis[0].plot(d, color=self.COLORS[i%len(self.COLORS)], label=v, zorder=1)
    #         self.axis[i+1].plot(d, color=self.COLORS[i%len(self.COLORS)], zorder=1)
    #         self.axis[i+1].set_ylabel(v)
    #         self.axis[i+1].autoscale(False)
    #         if d.max() > d.min():
    #             self.axis[i+1].set_ylim(d.max() - 1.05*(d.max() - d.min()), 1.05*d.max())
    #         self.axis[i+1].set_xlim(-0.05*len(self), 1.05*len(self))
    #     self.axis[0].autoscale(False)
    #     self.axis[0].set_xlim(-0.05*len(self), 1.05*len(self))
    #     self.axis[0].set_ylim(self.data.max() - 1.05*(self.data.max() - self.data.min()), 1.05*self.data.max())
    #     self.axis[-1].set_xlabel('Time')
    #     self.axis[0].set_ylabel(self.prefix)
    #     if plot_legend:
    #         self.axis[0].legend(fontsize=8, ncol=len(self.features) // 2)
    #     if make_title:
    #         self.figure.suptitle('%s' % self.title)
    #         plt.tight_layout()
    #     return self.figure, self.axis

class TPersInteract(TPers, Interact):
    def __init__(self, input_data, *args, **kwargs):
        self.input_data = input_data
        TPers.__init__(self, input_data, *args, **kwargs)
        self.plot()
        plt.show(block=False)
        Interact.__init__(self)
    def plot_frame(self, frame):
        if frame < len(self):
            self.last_frame = frame
            self.input_data.plot(frame, self.lim)
            self.plot_current(frame)
            plt.show(block=False)
        else:
            print(' ! Invalid frame')
    def get_closest(self, event):
        return min(max(int(np.round(event.xdata)),0), len(self)-1)
    def prompt(self):
        return '[ Plot frame (0-%d): ' % len(self)
    def plot_current(self, frame):
        while self.cur_frame_plt:
            self.cur_frame_plt.pop().remove()
        for d, ax in enumerate(self.axis[1:]):
            kwargs = {'color' : self.COLORS[d], 's' : 50, 'zorder' : 2}
            self.cur_frame_plt.append(ax.scatter([frame], [self.data[frame,d]], **kwargs))
            self.cur_frame_plt.append(self.axis[0].scatter([frame], [self.data[frame,d]], **kwargs))
        self.update_figure()


# class TPersInteract(TPers):
#     def __init__(self, input_data, *args, **kwargs):
#         self.input_data = input_data
#         TPers.__init__(self, input_data, *args, **kwargs)
#         self.cur_frame_plt = []
#         self.plot()
#         plt.show(block=False)
#         # self.frame_modules = {m for m,f in data_dict.items() if isinstance(f, FramedData)}
#         # self.cur_framed_data = {l : data_dict[l] for l in self.frame_modules.intersection(plot)}
#         # self.n_frames = len(self.data)
#         self.mouse_cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)
#         self.release_cid = self.figure.canvas.mpl_connect('button_release_event', self.onrelease)
#         self.key_cid = self.figure.canvas.mpl_connect('key_press_event', self.onpress)
#         self.last_frame, self.press_time = -1, None
#         frame = input('[ Plot frame (0-%d): ' % len(self))
#         while frame:
#             self.plot_frame(int(frame))
#             frame = input('[ Plot frame (0-%d): ' % len(self))
#         else:
#             input('[ Exit ]')
#     def plot_current(self, frame):
#         while self.cur_frame_plt:
#             self.cur_frame_plt.pop().remove()
#         for d, ax in enumerate(self.axis[1:]):
#             kwargs = {'color' : self.COLORS[d], 's' : 50, 'zorder' : 2}
#             self.cur_frame_plt.append(ax.scatter([frame], [self.data[frame,d]], **kwargs))
#             self.cur_frame_plt.append(self.axis[0].scatter([frame], [self.data[frame,d]], **kwargs))
#         self.figure.canvas.draw()
#         self.figure.canvas.flush_events()
#     def plot_frame(self, frame):
#         if frame < len(self):
#             self.last_frame = frame
#             self.input_data.plot(frame, self.lim)
#             self.plot_current(frame)
#             plt.show(block=False)
#         else:
#             print(' ! Invalid frame')
#     def onclick(self, event):
#         self.press_time = time.time()
#     def onrelease(self, event):
#         if (any(event.inaxes == ax for ax in self.axis)
#                 and self.press_time is not None and time.time() - self.press_time < 0.5):
#             frame = min(max(int(np.round(event.xdata)),0), len(self)-1)
#             sys.stdout.write('%d\n[ Plot frame (0-%d): ' % (frame, len(self)))
#             sys.stdout.flush()
#             self.plot_frame(frame)
#             self.figure.canvas.manager.window.activateWindow()
#             self.figure.canvas.manager.window.raise_()
#     def onpress(self, event):
#         if event.key == 'right':
#             frame = (self.last_frame+1) % len(self)
#         elif event.key == 'left':
#             frame = (self.last_frame-1) % len(self)
#         else:
#             return
#         sys.stdout.write('%d\n[ Plot frame (0-%d): ' % (frame, len(self)))
#         sys.stdout.flush()
#         self.plot_frame(frame)
#         self.figure.canvas.manager.window.activateWindow()
#         self.figure.canvas.manager.window.raise_()
