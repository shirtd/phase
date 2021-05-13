# from phase.plot import plot_diagrams, plt

from tqdm import tqdm
import numpy as np

class Data:
    module = 'input'
    args = []
    def __init__(self, data, name, title, prefix, features):
        self.data, self.features = data, features
        self.name, self.title, self.prefix = name, title, prefix
    def __iter__(self):
        yield from self.data
    def __repr__(self):
        return self.title
    def __getitem__(self, i):
        return self.data[i]
    def __len__(self):
        return len(self.data)

class MetricData(Data):
    module = 'input'
    args = []
    def __init__(self, data, name, title, prefix):
        features = ['Coord %d' % i for i in range(1,data.shape[-1]+1)]
        Data.__init__(self, data, name, title, prefix, features)

class PersistenceData(Data):
    module = 'persist'
    args = []
    def __init__(self, input_data, data, name, title, prefix, dim):
        self.dim, self.input_data = dim, input_data
        features = ['H%d' % d for d in range(dim+1)]
        Data.__init__(self, data, name, title, prefix, features)
        # self.lim = max(d if d < np.inf else b for dgms in data for dgm in dgms for b,d in dgm)
        # self.figure, self.axis = None, None
    def __call__(self, d, *args, **kwargs):
        pass
    def run(self, input_data, prefix, *args, **kwargs):
        return [self(d, *args, **kwargs) for d in tqdm(input_data, total=len(input_data), desc='[ %s persistence' % prefix)]
    # def plot(self, frame, lim=None):
    #     if self.figure is None or self.axis is None:
    #         self.figure, self.axis = plt.subplots(1,1)
    #     self.axis.cla()
    #     self.axis.autoscale(False)
    #     if lim is not None:
    #         self.axis.set_xlim(-0.05, 1.26*lim)
    #         self.axis.set_ylim(-0.05, 1.26*lim)
    #     plot_diagrams(self.axis, self[frame], lim)
    #     self.figure.suptitle('%s frame %d' % (self.title, frame), fontsize=8)
    #     plt.tight_layout()
    #     self.figure.canvas.draw()
    #     self.figure.canvas.flush_events()
    #     return self.figure, self.axis

# class TimeSeriesData(Data):
#     args = []
#     module = 'analyze'
#     def plot(self, data=None, features=None, figsize=(12,8), plot_legend=True, make_title=True):
#         values = self.values if values is None else values
#         data = (self.data if data is None else data)[:,[self.value_map[v] for v in values]]
#         if self.figure is not None or self.axis is not None:
#             plt.close(self.figure)
#         self.figure, self.axis = plt.subplots(len(values)+1,1, sharex=True, figsize=figsize)
#         for i, (d, v) in enumerate(zip(data.T, values)):
#             self.axis[0].plot(d, color=self.COLORS[i%len(self.COLORS)], label=v, zorder=1)
#             self.axis[i+1].plot(d, color=self.COLORS[i%len(self.COLORS)], zorder=1)
#             self.axis[i+1].set_ylabel(v)
#             self.axis[i+1].autoscale(False)
#             self.axis[i+1].set_xlim(-0.05*len(data), 1.05*len(data))
#         self.axis[0].autoscale(False)
#         self.axis[0].set_xlim(-0.05*len(data), 1.05*len(data))
#         if plot_anom:
#             lim = (data.max() - 1.05*(data.max() - data.min()), 1.05*data.max())
#             lims = list(zip(data.max(0) - 1.05*(data.max(0) - data.min(0)), 1.05*data.max(0)))
#             for l in self.anomalies:
#                 self.axis[0].plot([l,l],lim, ls=':', c='red', alpha=0.25, zorder=0)
#                 self.axis[0].set_ylim(*lim)
#                 for i,h in enumerate(lims):
#                     self.axis[i+1].plot((l,l), h, ls=':', c='red', alpha=0.25, zorder=0)
#                     self.axis[i+1].set_ylim(*h)
#         self.axis[-1].set_xlabel('Time')
#         self.axis[0].set_ylabel(self.prefix)
#         if plot_legend:
#             self.axis[0].legend(fontsize=8, ncol=len(values) // 2)
#         if make_title:
#             self.figure.suptitle('%s %s' % (self.prefix, self.title))
#             plt.tight_layout()
#         return self.figure, self.axis
