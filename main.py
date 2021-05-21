from phase.args import parser
from phase.base import InputData
from phase.tpers import TPers
from phase.complexes import AlphaComplexData, VoronoiComplexData
from phase.tda import Persistence, PersistenceReps
from phase.plot.interact import TPersInteract, \
                                TPersInteractBase, \
                                AlphaPersistenceInteract, \
                                VoronoiPersistenceInteract

from phase.plot.mpl import plt

import pickle as pkl
import os, sys, time


def try_cache(cls, input_args, *args, **kwargs):
    kwargs = {**{a : getattr(input_args, a) for a in cls.args}, **kwargs}
    name = cls.get_name(*args, **kwargs)
    fcache = os.path.join(input_args.cache, '%s.pkl' % name)
    if (not (input_args.nocache or cls.module in input_args.force)
            and os.path.exists(fcache)):
        print('[ loading %s' % fcache, end='')
        t0 = time.time()
        with open(fcache, 'rb') as f:
            dat = pkl.load(f)
            print(' %0.3fs' % (time.time() - t0))
            return dat
    dat = cls(*args, **kwargs)
    if not input_args.nocache:
        if not os.path.exists(input_args.cache):
            os.makedirs(input_args.cache)
        print('[ saving %s' % fcache, end='')
        t0 = time.time()
        with open(fcache, 'wb') as f:
            pkl.dump(dat, f)
            print(' %0.3fs' % (time.time() - t0))
    return dat

def filt_cls(args):
    return (VoronoiComplexData if args.dual
        else AlphaComplexData)

def pers_cls(args):
    return (PersistenceReps if args.reps
        else Persistence)

def pers_interact_cls(args):
    return (VoronoiPersistenceInteract if args.dual
        else AlphaPersistenceInteract)

if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'wrap':
        IPYTHON = True
        args = parser.parse_args(sys.argv[2].split())
    else:
        IPYTHON = False
        args = parser.parse_args()

    input_data = try_cache(InputData, args)

    if args.skip:
        comp, pers = complex_cls(args), pers_cls(args)
        comp_kw = {a : getattr(args, a) for a in comp.args}
        pers_kw = {a : getattr(args, a) for a in pers.args}
        name = pers.make_name(comp.get_name(input_data, **comp_kw), **pers_kw)
        fcache = os.path.join(args.cache, '%s.pkl' % name)
        print('[ Loading %s' % fcache)
        with open(fcache, 'rb') as f:
            pers_data = pkl.load(f)
    elif not args.nocomplex:
        filt_data = try_cache(filt_cls(args), args, input_data)

        if not args.nopers:
            pers_data = try_cache(pers_cls(args), args, filt_data)

    if (not args.nocomplex and not args.nopers) or args.skip:
        tpers_data = TPers(pers_data, **{a : getattr(args, a) for a in TPers.args})

        if args.interact:
            if args.reps:
                pers_interact = pers_interact_cls(args)(pers_data, filt_data, input_data)
                tpers_interact = TPersInteract(tpers_data, pers_data, pers_interact, args.histo)
            else:
                tpers_interact = TPersInteractBase(tpers_data, pers_data, args.histo)
        elif args.show:
            tpers_data.plot()
            plt.show(block=False)

    if (args.show or args.interact) and not IPYTHON:
        input('[ Exit ]')
