from phase.args import parser
from phase.base import InputData
from phase.util import load, save
from phase.filtration import filt_cls
from phase.tda import pers_cls, Persistence
from phase.plot.interact import TPersInteract, \
                                TPersInteractBase, \
                                pers_interact_cls
from phase.tpers import TPers

from phase.plot.mpl import plt

import os, sys, time


def get_kwargs(cls, args):
    return {a : getattr(args, a) for a in cls.args}

def try_cache(cls, input_args, *args, **kwargs):
    if cls is None:
        return
    kwargs = {**{a : getattr(input_args, a) for a in cls.args}, **kwargs}
    name = cls.get_name(*args, **kwargs)
    fcache = os.path.join(input_args.cache, '%s.pkl' % name)
    if (not (input_args.nocache or cls.module in input_args.force)
            and os.path.exists(fcache)):
        return load(fcache)
    dat = cls(*args, **kwargs)
    if not input_args.nocache:
        if not os.path.exists(input_args.cache):
            os.makedirs(input_args.cache)
        save(dat, fcache)
    return dat

def skip_filt(input_data, args):
    filt_t, pers_t = filt_cls(args), pers_cls(args) #Persistence
    filt_name = filt_t.get_name(input_data, **get_kwargs(filt_t, args))
    pers_name = pers_t.make_name(filt_name, **get_kwargs(pers_t, args))
    fcache = os.path.join(args.cache, '%s.pkl' % pers_name)
    if os.path.exists(fcache):
        return load(fcache)
    print(' ! %s is not cached' % fcache)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'wrap':
        IPYTHON = True
        args = parser.parse_args(sys.argv[2].split())
    else:
        IPYTHON = False
        args = parser.parse_args()

    input_data = try_cache(InputData, args)
    pers_data = None

    if args.nofilt and not args.nopers:
        pers_data = skip_filt(input_data, args)
        if pers_data is None:
            args.nofilt = False

    if not args.nofilt:
        filt_data = try_cache(filt_cls(args), args, input_data)

    if not args.nopers:
        if pers_data is None:
            pers_data = try_cache(pers_cls(args), args, filt_data)

        if args.interact or args.show or IPYTHON:
            tpers_data = TPers(pers_data, **get_kwargs(TPers, args))

            if args.interact:
                if args.reps and  not args.nofilt:
                    pers_interact = pers_interact_cls(args)(pers_data, filt_data, input_data)
                    tpers_interact = TPersInteract(tpers_data, pers_data, pers_interact, args.histo)
                else:
                    tpers_interact = TPersInteractBase(tpers_data, pers_data, args.histo)

            elif args.show:
                tpers_data.plot()
                plt.show(block=False)

            if not IPYTHON:
                input('[ Exit ]')
