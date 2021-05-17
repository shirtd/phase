from multiprocessing import Pool
from functools import partial
import numpy as np
import numpy.linalg as la
from itertools import combinations
# import matplotlib.pyplot as plt
# from matplotlib.patches import Circle
# from matplotlib.collections import PatchCollection
# from matplotlib import cm

def to_path(vertices, nbrs):
    V = vertices.copy()
    cur = V.pop()
    path = [cur]
    while len(V):
        cur = nbrs[cur].intersection(V).pop()
        path.append(cur)
        V.remove(cur)
    return path

def diff(p):
    return p[1] - p[0]

def identity(x):
    return x

def get_delta(n, w=1, h=1):
    return 2 / (n-1) * np.sqrt(w ** 2 + h ** 2)

def lipschitz(f, P):
    return max(abs(fp - fq) / la.norm(p - q) for (fp,p),(fq,q) in combinations(zip(f,P),2))

def scale(x):
    return (x - x.min()) / (x.max() - x.min())

def stuple(s, *args, **kw):
    return tuple(sorted(s, *args, **kw))

def pmap(fun, x, *args, **kw):
# def pmap(fun, x, max_cores=None, *args, **kw):
    pool = Pool(max_cores)
    f = partial(fun, *args, **kw)
    try:
        y = pool.map(f, x)
    except KeyboardInterrupt as e:
        print(e)
        pool.close()
        pool.join()
        sys.exit()
    pool.close()
    pool.join()
    return y

def format_float(f):
    if f.is_integer():
        return int(f)
    e = 0
    while not f.is_integer():
        f *= 10
        e -= 1
    return '%de%d' % (int(f), e)

# def ass1(dgm, d, w):
#     return all(w < p.birth or p.death < w or w + d < p.death for p in dgm)
#
# def ass2(dgm, d, w):
#     return all(p.birth <= w - d or w < p.birth or p.death < w for p in dgm)
#
# def check_ass(dgm, d, w):
#     return ass1(dgm, d, w) and ass2(dgm, d, w)
#
# def plot_dgm(axis, dgm, lim=None, omega=None, maxdim=None, clear=False, show=False):
#     if clear:
#         axis.cla()
#     lim = dgm.lim if lim is None else lim
#     if len(dgm.diagram):
#         maxdim = max(dgm.diagram) if maxdim is None else maxdim
#     else:
#         return
#     axis.plot([0, lim],[lim, lim], c='black', ls=':', alpha=0.5, zorder=0)
#     axis.plot([lim, lim],[lim, 2*lim], c='black', ls=':', alpha=0.5, zorder=0)
#     axis.plot([0, 2*lim], [0, 2*lim], c='black', zorder=0, alpha=0.5)
#     if omega is not None:
#         axis.plot([0, omega],[omega, omega], c='black', ls=':', alpha=0.5, zorder=0)
#         axis.plot([omega, omega],[omega, 2*lim], c='black', ls=':', alpha=0.5, zorder=0)
#     for dim in range(maxdim+1):
#         d = dgm.as_np(dim, lim)
#         axis.scatter(d[:,0], d[:,1], alpha=0.5, zorder=1, s=5,
#                         label='dim = %d (%d)' % (dim, len(dgm.get_inf(dim))))
#     handles, labels = axis.get_legend_handles_labels()
#     axis.legend(handles[::-1], labels[::-1], loc=4)
#     # axis.legend(loc=4)
#     if show:
#         plt.pause(0.1)
#
# def plot_dgm_dio(axis, dgm, lim=None, maxdim=None, clear=False, show=False):
#     if clear:
#         axis.cla()
#     lim = dgm.lim if lim is None else lim
#     axis.plot([0, lim],[lim, lim], c='black', ls=':', alpha=0.5, zorder=0)
#     axis.plot([lim, lim],[lim, 2*lim], c='black', ls=':', alpha=0.5, zorder=0)
#     axis.plot([0, 2*lim], [0, 2*lim], c='black', zorder=0, alpha=0.5)
#     for dim, dg in enumerate(dgm[:-1]):
#         if len(dg):
#             d = np.array([[p.birth, p.death if p.death < np.inf else 2*lim] for p in dg])
#         else:
#             d = np.ndarray((0,2), dtype=float)
#         axis.scatter(d[:,0], d[:,1], alpha=0.5, zorder=1, s=5, label='dim = %d' % dim)
#     axis.legend()
#     if show:
#         plt.pause(0.1)
#
# def plot_1_chain(axis, dgm, pt, color='blue', zorder=5, show=False, torus=True):
#     l = 2*np.pi
#     tiles = [[0,0],[l,0],[-l,0],[0,l],[0,-l],
#             [l,l],[-l,l],[-l,-l],[l,-l]]
#     chain = dgm.get_chain(pt)
#     if torus:
#         E = [dgm.F.points[list(s)] + s.offset for s in chain]
#         for e in E:
#             for a,b in tiles:
#                 axis.plot(e[:,0]+a, e[:,1]+b, c=color, zorder=zorder)
#     else:
#         E = [dgm.F.points[list(s)] for s in chain]
#         for e in E:
#             axis.plot(e[:,0], e[:,1], c=color, zorder=zorder)
#     if show:
#         plt.pause(0.1)
#
# def plot_2_boundary(axis, dgm, pt, color='red', zorder=5, show=False, torus=True):
#     l = 2*np.pi
#     tiles = [[0,0],[l,0],[-l,0],[0,l],[0,-l],
#             [l,l],[-l,l],[-l,-l],[l,-l]]
#     chain = dgm.get_chain(pt)
#     bdy = dgm.F.chain_boundary(chain)
#     if torus:
#         E = [dgm.F.points[list(s)] + s.offset for s in bdy]
#         for e in E:
#             for a,b in tiles:
#                 axis.plot(e[:,0]+a, e[:,1]+b, c=color, zorder=zorder)
#     else:
#         E = [dgm.F.points[list(s)] for s in bdy]
#         for e in E:
#             axis.plot(e[:,0], e[:,1], c=color, zorder=zorder)
#     if show:
#         plt.pause(0.1)
