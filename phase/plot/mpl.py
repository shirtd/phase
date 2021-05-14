from phase.plot.util import plot_diagrams

import matplotlib.pyplot as plt
import numpy as np

class MPLPlot:
    COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    def __init__(self, *fig_args, **fig_kwargs):
        self.fig_args, self.fig_kwargs = fig_args, fig_kwargs
        self.figure, self.axis = None, None
    def update_figure(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
    def raise_figure(self):
        self.figure.canvas.manager.window.activateWindow()
        self.figure.canvas.manager.window.raise_()
    def clear_fig(self, close=False):
        if close:
            if self.figure is not None:
                plt.close(self.figure)
            return self.init_fig()
        if self.figure is None or self.axis is None:
            return self.init_fig()
        self.axis.cla()
        return self.figure, self.axis
    def init_fig(self):
        self.figure, self.axis = plt.subplots(*self.fig_args, **self.fig_kwargs)
        return self.figure, self.axis
    def get_limits(self, mn, mx):
        return mx - 1.05*(mx - mn), 1.05*mx
    def scale_axis(self, axis, xmin, xmax, ymin, ymax):
        axis.autoscale(False)
        if xmax > xmin:
            axis.set_xlim(*self.get_limits(xmin, xmax))
        if ymax > ymin:
            axis.set_ylim(*self.get_limits(ymin, ymax))

class PersistencePlot(MPLPlot):
    def __init__(self):
        self.current_frame = None
        MPLPlot.__init__(self, 1, 1)
    def plot(self, frame, lim=None, dgm=None):
        fig, ax = self.clear_fig()
        lim, _ = plot_diagrams(ax, self[frame] if dgm is None else dgm, lim)
        self.scale_axis(ax, 0, 1.2*lim, 0, 1.2*lim)
        fig.suptitle('%s frame %d' % (self.title, frame), fontsize=8)
        plt.tight_layout()
        self.update_figure()
        self.current_frame = frame
        return fig, ax

class TimeSeriesPlot(MPLPlot):
    def plot(self, plot_legend=True, make_title=True):
        fig, ax = self.clear_fig(close=True)
        for i, (d, v) in enumerate(zip(self.data.T, self.features)):
            ax[0].plot(d, color=self.COLORS[i%len(self.COLORS)], label=v, zorder=1)
            ax[i+1].plot(d, color=self.COLORS[i%len(self.COLORS)], zorder=1)
            self.scale_axis(ax[i+1], 0, len(self), min(d), max(d))
        self.scale_axis(ax[0], 0, len(self), self.data.min(), self.data.max())
        ax[-1].set_xlabel('Time')
        ax[0].set_ylabel(self.prefix)
        if plot_legend:
            ax[0].legend(fontsize=8, ncol=len(self.features) // 2)
        if make_title:
            fig.suptitle('%s' % self.title)
            plt.tight_layout()
        return fig, ax
