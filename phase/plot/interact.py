from phase.plot.mpl import MPLPlot, plt
from phase.plot.pyv import ChainPlot
from phase.stats import PersHisto
from phase.data import BOUNDS
from functools import partial

from phase.topology.util import fill_birth, fill_death
from phase.topology.cells import DualComplex

import numpy.linalg as la
import numpy as np
import time, sys


COLORS = { 'points' : 'white',
            'edges' : '#f7f7f7',#'#386cb0',#'#8da0cb',#'#a6cee3',#'#f7f7f7',#'#ece7f2',
            'faces' : '#f4a582',#'#fb9a99',#'#f4a582',#'#2b8cbe',
            'dual' : 'black',
            'primal birth' : '#1a9641',#'#0571b0',#'#b2df8a', #'#4daf4a',
            'primal death' : '#ca0020',#'#fb9a99'}#'#e41a1c'}
            'dual birth' : '#0571b0',
            'dual death' : '#e66101'}

KWARGS = { 'points' : {'radius' : 0.02, 'color' : COLORS['points']},
            'dual' : {'radius' : 0.02, 'color' : COLORS['dual']},
            'edges' : {'radius' : 0.005, 'color' : COLORS['edges']},
            'faces' : {'opacity' : 0.05, 'color' : COLORS['faces']},
            'primal birth' : {'color' : COLORS['primal birth']},
            'primal death' : {'color' : COLORS['primal death']},
            'dual birth' : {'color' : COLORS['dual birth']},
            'dual death' : {'color' : COLORS['dual death']}}


class Interact:
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
        self.histo = PersHisto(data, value) if value is not None else None
        self.trace_start = None
        self.sub = sub
        self.data.plot()
        plt.show(block=False)
        self.connect()
        # self.run()
        self.plot_frame(0)
    def plot_frame(self, frame):
        if frame < len(self.data):
            self.last_frame = frame
            if self.sub is None:
                self.data.input_data.plot(frame, self.data.lim)
            else:
                self.sub.plot(frame, self.data.lim, self.data)
                if self.trace_start is not None:
                    self.sub.plot_trace(self.trace_start, frame)
                # self.histo(frame, self.sub.active_dgm)
            if self.histo is not None:
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
    def onpress(self, event):
        if self.sub is not None and event.key == 't':
            if self.trace_start is not None:
                print('* trace off')
                self.trace_start = None
                self.sub.remove('trace')
            else:
                print('* trace on')
                self.sub.remove('trace')
                self.trace_start = self.last_frame
        return Interact.onpress(self, event)


class MyPersistenceChainPlot(ChainPlot):
    def __init__(self, data):
        ChainPlot.__init__(self, data)
        self.data.init_fig()
        self.dual = None
        self.dgm = None
        self.last_frame = None
        self.trace_points = {'primal' : None, 'dual' : None}
        self.trace_edges = {'primal' : None, 'dual' : None}
        self.options = {'dgm' : {'primal' : True, 'dual' : False, 'filled' : True},
                        'complex' : {'primal' : {0 : True, 1 : True, 2 : True},
                                        'dual' : {0 : False, 1 : False, 2 : False}},
                        'trace' : {'primal' : False, 'dual' : False}}
        self.config = {'dgm' : {'primal' : {'birth' : KWARGS['primal birth'],
                                            'death' : KWARGS['primal death']},
                                'dual' : {'birth' : KWARGS['dual birth'],
                                            'death' : KWARGS['dual death']}},
                        'complex' : {'primal' : {0 : KWARGS['points'],
                                                1 : KWARGS['edges'],
                                                2 : KWARGS['faces']},
                                    'dual' : {0 : {**KWARGS['points'], **{'color' : 'black'}},
                                                1 : {**KWARGS['edges'], **{'color' : '#404040'}},
                                                2 : {**KWARGS['faces'], **{'color' : '#c2a5cf'}}}},
                        'trace' : {'primal' : {'color' : '#ffff99', 'radius' : None}}}
        self.key_events = { 'x' : self.reset,
                            'z' : self.reset_view,
                            'p' : partial(self.toggle, 'dgm', 'primal'),
                            'd' : partial(self.toggle, 'dgm', 'dual'),
                            'c' : partial(self.toggle, 'dgm', 'filled'),
                            '0' : partial(self.toggle, 'complex', 'primal', 0),
                            '6' : partial(self.toggle, 'complex', 'dual', 0),
                            '1' : partial(self.toggle, 'complex', 'primal', 1),
                            '5' : partial(self.toggle, 'complex', 'dual', 1),
                            '2' : partial(self.toggle, 'complex', 'primal', 2),
                            '4' : partial(self.toggle, 'complex', 'dual', 2),
                            '8' : partial(self.toggle, 'complex', 'primal', 0, 1, 2, force=True),
                            # '6' : partial(self.toggle, 'complex', 'dual', 0, 1, 2, force=True),
                            '9' : partial(self.toggle, 'complex', 'primal', 0, 1, 2, force=False),
                            '7' : partial(self.toggle, 'complex', 'dual', 0, 1, 2, force=False)}#,
                            # 'y' : self.query_range}
        self.min, self.max = -np.inf, np.inf
    def in_range(self, s):
        return self.min < self.dgm.F(s) < self.max
    def query_range(self):
        pass
    def plot(self, frame):
        self.remove()
        self.dgm = self.data.chain_data[frame]
        self.init_dual()
        self.plot_complex()
    def plot_trace(self, a, b):
        if a == b:
            self.remove('trace')
        else:
            a, b = (a, b) if a < b else (b, a)
            Ps = self.data.input_data[a:b+1]
            n = min(len(P) for P in Ps)
            E = []
            for i in range(n):
                for k in range(1, len(Ps)):
                    if (not (self.data.is_boundary(Ps[k-1][i])
                            or self.data.is_boundary(Ps[k][i]))):
                        E.append([i + (k-1)*n, i + k*n])
            self.plot_curves(np.vstack(Ps), E, 'trace', **self.config['trace']['primal'])
    def init_fig(self):
        fig = ChainPlot.init_fig(self)
        self.reset_view()
        for k, f in self.key_events.items():
            fig.add_key_event(k, f)
        fig.enable_parallel_projection()
        fig.add_key_event('i', fig.isometric_view)
        return fig
    def reset_view(self):
        l = (BOUNDS[1] - BOUNDS[0]) / 2
        self.figure.camera_position = [(30,l,l), (l,l,l), (0,0,1)]
        self.figure.camera_position = [(l*l,l*l,l*l), (l,l,l), (0,0,1)]
        # self.figure.isometric_view()
        self.figure.camera_set = True
    def reset(self):
        self.remove(keep={'trace'})
        self.plot_complex()
    def toggle(self, key, toggle, *args, force=None):
        opts, cfg = self.options[key], self.config[key]
        if key == 'dgm' and self.last_frame is not None:
            opts[toggle] = not opts[toggle] if force is None else force
            self.plot_rep(self.last_frame, opts, cfg)
        elif key == 'complex':
            for dim in args:
                opts[toggle][dim] = not opts[toggle][dim] if force is None else force
                self.plot_complex(opts, cfg)

    def get_simplices(self, pd, dim):
        if pd == 'primal':
            Kd = self.dgm.F.K[dim]
            return [s for s in Kd if not self.dgm.is_relative(s) and self.in_range(s)]
        elif pd == 'dual':
            Kd = self.dgm.F.K[self.dgm.F.dim - dim]
            return [self.get_dual(s) for s in Kd if not self.dgm.is_relative(s) and self.in_range(s)]
    def plot_complex(self, opts=None, cfg=None):
        opts = self.options['complex'] if opts is None else opts
        cfg = self.config['complex'] if cfg is None else cfg
        for pd, opt in opts.items():
            for dim, tog in opt.items():
                key = '%s%d' % (pd, dim)
                if tog:
                    S = self.get_simplices(pd, dim)
                    K = self.dgm.F.K if pd == 'primal' else self.dual
                    self.plot_chain(S, dim, key, K, **cfg[pd][dim])
                else:
                    self.remove(key)
    def plot_rep(self, i, opts=None, cfg=None):
        opts = self.options['dgm'] if opts is None else opts
        cfg = self.config['dgm'] if cfg is None else cfg
        s = self.get_simplex(i)
        if opts['primal'] or opts['dual']:
            K, B = self.dgm.F.K, self.dgm.D[i]
            bdim, ddim = s.dim, self.get_simplex(self.dgm[i]).dim
            D = fill_death(self.dgm, i) if opts['filled'] else self.dgm.D[self.dgm[i]]
            if opts['primal']:
                self.plot_chain(B, bdim, 'primal birth', K, **cfg['primal']['birth'])
                self.plot_chain(D, ddim, 'primal death', K, **cfg['primal']['death'])
            if opts['dual']:
                B = fill_birth(self.dgm, i) if opts['filled'] else self.dgm.D[i]
                D = self.dgm.D[self.dgm[i]]
                dbdim, dddim = K.dim - bdim, K.dim - ddim
                dB, dD = [self.get_dual(s) for s in B], [self.get_dual(s) for s in D]
                self.plot_chain(dB, dbdim, 'dual birth', self.dual, **cfg['dual']['birth'])
                self.plot_chain(dD, dddim, 'dual death', self.dual, **cfg['dual']['death'])
        if not opts['primal']:
            self.remove('primal birth')
            self.remove('primal death')
        if not opts['dual']:
            self.remove('dual birth')
            self.remove('dual death')
    def init_dual(self):
        pass
    def get_dual(self, i):
        pass


class MyPersistenceInteract(Interact, MyPersistenceChainPlot):
    def __init__(self, data):
        Interact.__init__(self, data)
        MyPersistenceChainPlot.__init__(self, data)
        self.active_pairs = {}
        self.sorted_births = []
        self.connect()
    def onpress(self, event):
        for k, f in self.key_events.items():
            if event.key == k:
                f()
        if self.last_frame is None:
            return self.plot_frame()
        Interact.onpress(self, event)
    def plot(self, frame, lim, tpers_data):
        MyPersistenceChainPlot.plot(self, frame)
        self.active_dgms = [tpers_data.get_range(dgm) for dgm in self.data[frame]]
        self.active_pairs = {b : d for b,d in self.dgm.items() if tpers_data.inrng(self.dgm(b))}
        self.sorted_births = sorted(self.active_pairs, key=lambda b: self.dgm.persistence(b), reverse=True)
        self.birth_imap = {b : i for i,b in enumerate(self.sorted_births)}
        self.last_frame = None
        return self.data.plot(frame, lim, self.active_dgms)
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
        dst = lambda s: la.norm(p - self.dgm(s))
        return min([b for b in self.active_pairs], key=dst)
    def plot_current(self, i):
        while self.cur_frame_plt:
            self.cur_frame_plt.pop().remove()
        s = self.dgm.F[i]
        p = self.dgm(i)
        self.cur_frame_plt.append(self.data.axis.scatter(p[0], p[1], s=50, color=self.data.COLORS[s.dim], zorder=2))
        self.data.update_figure()
    def get_next(self):
        return self.sorted_births[(self.birth_imap[self.last_frame]+1) % len(self.sorted_births)]
    def get_prev(self):
        return self.sorted_births[(self.birth_imap[self.last_frame]-1) % len(self.sorted_births)]

class AlphaPersistenceInteract(MyPersistenceInteract):
    is_dual = False
    def init_dual(self):
        self.dual = DualComplex(self.dgm.F.K, 'alpha')
    def get_dual(self, s):
        return self.dual(s)

class VoronoiPersistenceInteract(MyPersistenceInteract):
    is_dual = True
    def init_dual(self):
        self.dual = self.dgm.F.K.K
    def get_dual(self, s):
        return self.dgm.F.K.pmap[s]

    # def toggle(self, opt):
    #     self.options[opt] = not self.options[opt]
    #     self.plot_rep(self.last_frame)
    # def plot_cloud(self, force=False):
    #     if 'points' in self.elements and not force:
    #         self.remove('points')
    #     elif self.dualized:
    #         self.plot_points(self.dual.P, 'points', **KWARGS['dual'])
    #     else:
    #         self.plot_points(self.get_points(), 'points', **KWARGS['points'])
    # def plot_cells(self, dim, force=False, **kwargs):
    #     key = 'K%d' % dim
    #     if key in self.elements and not force:
    #         self.remove(key)
    #     else:
    #         S = [s for s in self.dgm.F.K[dim] if not self.dgm.is_relative(s)]
    #         self.plot_chain(S, dim, key, **kwargs)
    # def plot_rep(self, i):
    #     s = self.get_simplex(i)
    #     if self.dualized:
    #         B, D = self.get_dual(i)
    #         bdim = self.dgm.F.dim - s.dim
    #         ddim = bdim - 1
    #         K = self.dual
    #     else:
    #         B = self.dgm.D[i]
    #         D = fill_death(self.dgm, i) if self.filled else self.dgm.D[self.dgm[i]]
    #         bdim, ddim = s.dim, self.get_simplex(self.dgm[i]).dim
    #         K = self.dgm.F.K
    #     self.plot_chain(B, bdim, 'birth', K, **KWARGS['birth'])
    #     self.plot_chain(D, ddim, 'death', K, **KWARGS['death'])
    #     # self.plot_cycle(i, 'birth', **KWARGS['birth'])
    #     # self.plot_cycle(self[i], 'death', **KWARGS['death'])
    # # def plot_rep(self, i):
    # #     self.dualized = False
    # #     self.filled = False
    # #     # self.plot_cloud()
    # #     self.plot_cycle(i, 'birth', **KWARGS['birth'])
    # #     self.plot_cycle(self[i], 'death', **KWARGS['death'])
    # # def fill_birth_cycle(self):
    # #     self.fill_birth = not self.fill_birth
    # #     self.pre_death = not self.pre_death
    # #     # self.filled = True
    # #     # if self.dualized:
    # #     #     return self.plot_dual(True)
    # #     return self.fill_cycle(True)
    # # def plot_all(self, dim):
    # #     sorted_births = [b for b in self.sorted_births if self.dgm.F[b].dim == dim]
    # #     if len(sorted_births):
    # #         B = self.dgm.D[sorted_births[0]]
    # #         D, added = _fill_death(self.dgm, sorted_births[0])
    # #         for b in sorted_births[1:]:
    # #             if not b in added:
    # #                 B = B + self.dgm.D[b]
    # #                 _D, _added = _fill_death(self.dgm, b)
    # #                 D = D + _D
    # #                 added = added.union(_added)
    # #         ddim = dim + 1
    # #         B = [s for s in B if not self.dgm.F.index(s) in self.dgm.R]
    # #         if len(B):
    # #             self.plot_chain(self.get_points(), self.format_cycle(B, dim), dim, 'birth', **KWARGS['birth'])
    # #         D = [s for s in D if not self.dgm.F.index(s) in self.dgm.R]
    # #         if len(D):
    # #             self.plot_chain(self.get_points(), self.format_cycle(D, ddim), ddim, 'death', **KWARGS['death'])
    # # def fill_cycle(self, force=False):
    # #     if self.last_frame is None:
    # #         return
    # #     if self.filled and not force:
    # #         if self.dualized:
    # #             self.filled = False
    # #             return self.plot_dual(True)
    # #         return self.plot_rep(self.last_frame)
    # #     self.filled = True
    # #     if self.dualized:
    # #         return self.plot_dual(True)
    # #     B = self.dgm.D[self.last_frame]
    # #     D = fill_death(self.dgm, self.last_frame)
    # #     bs = self.get_simplex(self.last_frame)
    # #     ds = self.get_simplex(self[self.last_frame])
    # #     # self.plot_cloud()
    # #     self.plot_chain(self.get_points(), self.format_cycle(B, bs.dim), bs.dim, 'birth', **KWARGS['birth'])
    # #     self.plot_chain(self.get_points(), self.format_cycle(D, ds.dim), ds.dim, 'death', **KWARGS['death'])
    # # def plot_dual(self, force=False):
    # #     if self.last_frame is None:
    # #         return
    # #     if self.dualized and not force:
    # #         if self.filled:
    # #             self.dualized = False
    # #             if 'points' in self.elements:
    # #                 self.plot_cloud(True)
    # #             return self.fill_cycle(True)
    # #         return self.plot_rep(self.last_frame)
    # #     self.dualized = True
    # #     s = self.get_simplex(self.last_frame)
    # #     dB, dD = self.get_dual(self.last_frame)
    # #     bdim = self.dgm.F.dim - s.dim
    # #     ddim, P = bdim - 1, self.dual.P
    # #     b = self.format_cycle(dB, bdim, self.dual)
    # #     d = self.format_cycle(dD, ddim, self.dual)
    # #     if 'points' in self.elements:
    # #         self.plot_cloud(True)
    # #     self.plot_chain(P, b, bdim, 'birth', **KWARGS['birth'])
    # #     self.plot_chain(P, d, ddim, 'death', **KWARGS['death'])
