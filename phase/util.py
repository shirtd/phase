from functools import partial, reduce
from itertools import combinations
from multiprocessing import Pool
import numpy.linalg as la
import pickle as pkl
import numpy as np
import sys, time, gc


def load(fcache):
    sys.stdout.write('[ loading %s...' % fcache)
    sys.stdout.flush()
    t0 = time.time()
    with open(fcache, 'rb') as f:
        gc.disable()
        dat = pkl.load(f)
        gc.enable()
    print(' %0.3fs' % (time.time() - t0))
    return dat

def save(dat, fcache):
    sys.stdout.write('[ saving %s...' % fcache)
    sys.stdout.flush()
    t0 = time.time()
    with open(fcache, 'wb') as f:
        gc.disable()
        pkl.dump(dat, f)
        gc.enable()
    print(' %0.3fs' % (time.time() - t0))


def insert(L, i, x):
    L[i] += [x]
    return L

def partition(f, X, n):
    return reduce(f, X, [[] for _ in range(n)])

def is_boundary(p, d, l):
    return not all(d < c < u - d for c,u in zip(p, l))

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
    pool = Pool()
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
