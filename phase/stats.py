from phase.plot.mpl import MPLPlot, plt

import numpy as np

class PersHisto(MPLPlot):
    def __init__(self, input_data, value, nbins=100):
        self.nbins, self.value = nbins, value
        self.fvalue = {'tpers' : lambda p: p[1] - p[0],
                        'birth' : lambda p: p[0],
                        'death' : lambda p: p[1]}
        ps = [self.fvalue[value](p) for dgms in input_data.input_data for dgm in dgms for p in dgm if p[1] < np.inf]
        self.vmin, self.vmax = min(ps), min(max(ps), input_data.lim)
        self.ymax = 500 # input_data.data.max() / self.vmax
        self.current_frame = None
        self.input_data = input_data
        MPLPlot.__init__(self)
    def __call__(self, frame, dgms):
        self.current_frame = frame
        L = np.linspace(self.vmin, self.vmax, self.nbins)
        bins = list(zip(L[:-1],L[1:])) + [(self.vmax, np.inf)]
        histos = [self.get_histo(dgm, bins, self.value) for dgm in dgms]
        self.plot(histos, L)
        return histos, L
    def get_histo(self, data, bins, value):
        histo = [[] for _ in bins]
        for p in data:
            for i, (a,b) in enumerate(bins):
                if a <= self.fvalue[value](p) < b:
                    histo[i].append(p)
        return [len(bin) for bin in histo]
    def plot(self, histos, L):
        fig, ax = self.clear_fig()
        for histo in histos:
            ax.plot(L - 1 / (self.nbins+1), histo)
        ax.set_ylim(0, self.ymax)
        fig.suptitle('%s histo, %s frame %d' % (self.value, self.input_data, self.current_frame), fontsize=8)
        plt.tight_layout()
        self.update_figure()
        return fig, ax


# def getL(R, n=100, pmin=None, pmax=None):
#     if pmin is None:
#         pmin = min(d - b for dgm in R['dgms'] for b,d in dgm if d < np.inf)
#     if pmax is None:
#         pmax = max(d - b for dgm in R['dgms'] for b,d in dgm if d < np.inf)
#     return np.linspace(pmin, pmax, n+1)
#
# def get_histo(R, L, stat='count'):
#     bins = list(zip(L[:-1], L[1:]))
#     histo = [[[] for _ in bins] for _ in R['dgms']]
#     tpers = get_tpers(R['dgms'])
#     for dim, dgm in enumerate(R['dgms']):
#         for b, d in dgm:
#             if d < np.inf:
#                 for i, (s,t) in enumerate(bins):
#                     if s <= d - b < t:
#                         histo[dim][i].append((b,d))
#     if stat == 'count':
#         return [[len(bin) for bin in h] for h in histo]
#     elif stat == 'percent':
#         return [[100 * sum(d - b for b,d in bin) / tot for bin in h] for tot,h in zip(tpers, histo)]
#
# def plot_histo(axis, L, histo, name='', ymax=None, stat='count'):
#     if ymax is not None:
#         ax.set_ylim(0, ymax)
#     for dim, h in enumerate(histo):
#         axis.plot(L[1:] - 1 / (args.bins+1), h, label='H%d' % dim)
#     fig.suptitle('TPers histogram %s' % name)
#     ax.set_xlabel('TPers')
#     ax.set_ylabel(stat)
#     ax.legend()
#     plt.tight_layout()
#
#
# if args.frame is not None:
#     P, R = Ps[args.frame], Rs[args.frame]
#     name = os.path.splitext(os.path.basename(args.file))[0]
#
#     L = getL(R, args.bins, args.pmin, args.pmax)
#     histo = get_histo(R, L)
#     plot_histo(ax, L, histo, '%s frame %d' % (name, args.frame), stat=args.stat)
#
# else:
#     if args.pmin is None:
#         args.pmin = min(d - b for R in Rs for dgm in R['dgms'] for b,d in dgm if d < np.inf)
#     if args.pmax is None:
#         args.pmax = max(d - b for R in Rs for dgm in R['dgms'] for b,d in dgm if d < np.inf)
#     L = np.linspace(args.pmin, args.pmax, args.bins+1)
#     histos = [get_histo(R, L, args.stat) for R in tqdm(Rs)]
#     if args.batch is not None:
#         histos = np.array(histos)
#         _histos = []
#         for i in range(len(histos) // args.batch):
#             s,t = i*args.batch, (i+1)*args.batch
#             _histos.append([[sum(histos[s:t,dim,bin]) / args.batch for bin in range(args.bins)] for dim in range(args.dim+1)])
#         histos = _histos
#     ymax = max(l for histo in histos for h in histo for l in h)
#     for frame, histo in tqdm(list(enumerate(histos))):
#         name = os.path.splitext(os.path.basename(args.file))[0]
#         frame = str(frame) if args.batch is None else '%d-%d' % (frame*args.batch, (frame+1)*args.batch-1)
#         plot_histo(ax, L, histo, '%s %s frame %s' % (args.stat, name, frame), ymax, stat=args.stat)
#         if args.out:
#             dout = os.path.join(args.out, name)
#             if not os.path.exists(dout):
#                 os.mkdir(dout)
#             if args.batch is not None:
#                 dout = os.path.join(dout, 'batch%d' % args.batch)
#             else:
#                 dout = os.path.join(dout, 'all')
#             if not os.path.exists(dout):
#                 os.mkdir(dout)
#             fout = os.path.join(dout, '%s_%s' % (args.stat, frame))
#             plt.savefig(fout, dpi=500)
#             ax.cla()
