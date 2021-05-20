from phase.plot.mpl import MPLPlot, plt
from phase.plot.pyv import ChainPlot
from phase.stats import PersHisto
from functools import partial

from phase.topology.util import fill_birth, fill_death
from phase.topology.cells import DualComplex

import numpy.linalg as la
import numpy as np
import time, sys


COLORS = { 'points' : 'white',
            'edges' : '#f7f7f7',
            'faces' : '#f4a582',
            'dual' : 'black',
            'primal birth' : '#1a9641',
            'primal death' : '#ca0020',
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

class TPersInteractBase(Interact):
    def __init__(self, data, value):
        Interact.__init__(self, data)
        self.histo = PersHisto(data, value) if value is not None else None
        self.data.plot()
        plt.show(block=False)
        self.connect()
        self.plot_frame(0)
    def plot_sub(self, frame):
        self.data.input_data.plot(frame, self.data.lim)
    def plot_histo(self, frame):
        if self.histo is not None:
            self.histo(frame, self.data.input_data[frame])
    def plot_frame(self, frame):
        if frame < len(self.data):
            self.last_frame = frame
            self.plot_sub(frame)
            self.plot_histo(frame)
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

class TPersInteract(TPersInteractBase):
    def __init__(self, data, sub=None, value='tpers'):
        self.sub, self.trace_start = sub, None
        TPersInteractBase.__init__(self, data, value)
    def plot_sub(self, frame):
        self.sub.plot(frame, self.data.lim, self.data)
        if self.trace_start is not None:
            self.sub.plot_trace(self.trace_start, frame)
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
        ChainPlot.__init__(self, data, data.bounds.max(0))
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
                    if (not (self.data.is_boundary(a+k-1, Ps[k-1][i])
                            or self.data.is_boundary(a+k, Ps[k][i]))):
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
        center = self.bounds / 2
        self.figure.camera_position = [(center[0] * 10, center[1], center[2]), center, (0, 0, 1)]
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
