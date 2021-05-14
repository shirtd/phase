from phase.base import Data
from phase.plot.mpl import TimeSeriesPlot
from phase.plot.interact import Interact

import matplotlib.pyplot as plt
import numpy as np


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
        self.input_data = input_data
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

class TPersInteract(Interact):
    def __init__(self, data):#, input_data):
        Interact.__init__(self, data)
        # self.input_data = input_data
        # self.input_data = input_data
        # TPers.__init__(self, input_data, *args, **kwargs)
        self.data.plot()
        plt.show(block=False)
        # Interact.__init__(self)
        self.connect()
        self.run()
    def plot_frame(self, frame):
        if frame < len(self.data):
            self.last_frame = frame
            self.data.input_data.plot(frame, self.data.lim)
            self.plot_current(frame)
            plt.show(block=False)
        else:
            print(' ! Invalid frame')
    def get_closest(self, event):
        return min(max(int(np.round(event.xdata)),0), len(self.data)-1)
    # def prompt(self):
    #     return '[ Plot frame (0-%d): ' % len(self)
    def plot_current(self, frame):
        while self.cur_frame_plt:
            self.cur_frame_plt.pop().remove()
        for d, ax in enumerate(self.data.axis[1:]):
            kwargs = {'color' : self.data.COLORS[d], 's' : 50, 'zorder' : 2}
            self.cur_frame_plt.append(ax.scatter([frame], [self.data[frame,d]], **kwargs))
            self.cur_frame_plt.append(self.data.axis[0].scatter([frame], [self.data[frame,d]], **kwargs))
        self.data.update_figure()

# class TPersInteract(TPers, Interact):
#     def __init__(self, input_data, *args, **kwargs):
#         self.input_data = input_data
#         TPers.__init__(self, input_data, *args, **kwargs)
#         self.plot()
#         plt.show(block=False)
#         Interact.__init__(self)
#         self.connect()
#         self.run()
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
#     # def prompt(self):
#     #     return '[ Plot frame (0-%d): ' % len(self)
#     def plot_current(self, frame):
#         while self.cur_frame_plt:
#             self.cur_frame_plt.pop().remove()
#         for d, ax in enumerate(self.axis[1:]):
#             kwargs = {'color' : self.COLORS[d], 's' : 50, 'zorder' : 2}
#             self.cur_frame_plt.append(ax.scatter([frame], [self.data[frame,d]], **kwargs))
#             self.cur_frame_plt.append(self.axis[0].scatter([frame], [self.data[frame,d]], **kwargs))
#         self.update_figure()
