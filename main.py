from phase.args import parser
from phase.data import *
from phase.tda import *
from phase.tpers import *
from phase.simplicial import Chain
from phase.plot.interact import TPersInteract, AlphaPersistenceInteract

from phase.plot.util import plot_diagrams

import pickle as pkl

# plt.ion()

def try_cache(cls, input_args, *args, **kwargs):
    kwargs = {**{a : getattr(input_args, a) for a in cls.args}, **kwargs}
    name = cls.get_name(*args, **kwargs)
    fcache = os.path.join(input_args.cache, '%s.pkl' % name)
    if not cls.module in input_args.force and os.path.exists(fcache):
        print('[ Loading %s' % fcache)
        with open(fcache, 'rb') as f:
            return pkl.load(f)
    dat = cls(*args, **kwargs)
    try:
        if not os.path.exists(input_args.cache):
            os.makedirs(input_args.cache)
        with open(fcache, 'wb') as f:
            pkl.dump(dat, f)
    except RecursionError as err:
        print(err)
    return dat

def fill_chain(dgm, birth, C=None):
    C = dgm.D[dgm.pairs[birth]] if C is None else C
    diff = dgm.F.boundary(C) + dgm.D[birth]
    if len(diff):
        p = max(dgm.F.index(s) for s in dgm.F.boundary(C) + dgm.D[birth])
        if p in dgm.pairs:
            return fill_chain(dgm, birth, C + dgm.D[dgm.pairs[p]])
    return C


if __name__ == '__main__':
    args = parser.parse_args()
    # args = parser.parse_args('--interact --force persist'.split())
    # args = parser.parse_args('--interact'.split())

    input_data = try_cache(InputData, args)

    # alpha_cls = AlphaPersistenceInteract if args.interact else
    pers_cls = RipsPersistence if args.rips else AlphaPersistence
    pers_data = try_cache(pers_cls, args, input_data)

    tpers = TPers(pers_data, **{a : getattr(args, a) for a in TPers.args})

    if args.interact:
        pers_interact = AlphaPersistenceInteract(pers_data) if not args.rips else None
        tpers_interact = TPersInteract(tpers, pers_interact)

    if args.show:
        plt.show(block=False)
        input('[ Exit ]')
