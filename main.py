from phase.args import parser
from phase.base import InputData
from phase.tpers import TPers
from phase.tda import RipsPersistence, \
                        AlphaPersistence, \
                        VoronoiPersistence
from phase.plot.interact import TPersInteract, \
                                AlphaPersistenceInteract, \
                                VoronoiPersistenceInteract

from phase.plot.mpl import plt

import pickle as pkl
import os, sys


def try_cache(cls, input_args, *args, **kwargs):
    kwargs = {**{a : getattr(input_args, a) for a in cls.args}, **kwargs}
    name = cls.get_name(*args, **kwargs)
    fcache = os.path.join(input_args.cache, '%s.pkl' % name)
    if not cls.module in input_args.force and os.path.exists(fcache):
        try:
            print('[ Loading %s' % fcache)
            with open(fcache, 'rb') as f:
                return pkl.load(f)
        except Exception as err:
            raise err
    dat = cls(*args, **kwargs)
    if not os.path.exists(input_args.cache):
        os.makedirs(input_args.cache)
    with open(fcache, 'wb') as f:
        pkl.dump(dat, f)
    return dat

def pers_cls(args):
    return (RipsPersistence if args.rips
        else VoronoiPersistence if args.dual
        else AlphaPersistence)

def pers_interact_cls(args):
    return (None if args.rips
        else VoronoiPersistenceInteract if args.dual
        else AlphaPersistenceInteract)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'wrap':
        IPYTHON = True
        args = parser.parse_args(sys.argv[2].split())
    else:
        IPYTHON = False
        args = parser.parse_args()

    input_data = try_cache(InputData, args)
    pers_data = try_cache(pers_cls(args), args, input_data)
    tpers = TPers(pers_data, **{a : getattr(args, a) for a in TPers.args})

    if args.interact:
        pers_interact = pers_interact_cls(args)(pers_data)
        tpers_interact = TPersInteract(tpers, pers_interact, args.histo)
    elif args.show:
        tpers.plot()

    if (args.show or args.interact) and not IPYTHON:

        plt.show(block=False)
        input('[ Exit ]')
