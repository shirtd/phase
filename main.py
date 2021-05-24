from phase.args import parser
from phase.data import FRAMES
from phase.base import InputData
from phase.util import load, save
from phase.filtration import filt_cls
from phase.tda import pers_cls, Persistence
from phase.plot.interact import TPersInteract, \
                                TPersInteractBase, \
                                pers_interact_cls
from phase.tpers import TPers

from phase.plot.mpl import plt

import os, sys, time, re, glob


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

def get_name(input_name, args):
    filt_t, pers_t = filt_cls(args), pers_cls(args) #Persistence
    filt_name = filt_t.make_name(input_name, **get_kwargs(filt_t, args))
    return pers_t.make_name(filt_name, **get_kwargs(pers_t, args))

def skip_filt(input_name, args):
    pers_name = get_name(input_name, args)
    fcache = os.path.join(args.cache, '%s.pkl' % pers_name)
    if os.path.exists(fcache):
        return load(fcache)
    print(' ! %s is not cached' % fcache)

def load_range(input_data, args):
    kwargs = get_kwargs(InputData, args)
    kwargs['frames'] = ('*', '*')
    input_name = input_data.get_name(**kwargs)
    name = get_name(input_name, args)
    gx = os.path.join(args.cache, '%s.pkl' % name)
    rx = gx.replace('*', '(.*)')
    fdict = {tuple(map(int, re.findall(rx, f)[0])) : f for f in glob.glob(gx)}
    imap, unavail, intervals = {}, [], set()
    for i in range(*input_data.frames):
        L = list(filter(lambda l: l[0] <= i < l[1], fdict.keys()))
        if L:
            imap[i] = max(L, key=lambda l: l[1]-l[0])
            intervals.add(imap[i])
        else:
            unavail.append(i)
    if unavail:
        print(' ! unable to load frames %s' % ', '.join(map(str,unavail)))
    if not intervals:
        print(' ! could not find any frames. aborting.')
        return None
    pers_datas = [load(fdict[l]) for l in sorted(intervals)]
    pers_data = pers_datas[0]
    pers_data.data = [d for D in pers_datas for d in D]
    return pers_data

if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'wrap':
        IPYTHON = True
        args = parser.parse_args(sys.argv[2].split())
    else:
        IPYTHON = False
        args = parser.parse_args()

    if args.preset is not None:
        if args.preset == 'generate':
            args.parallel = True
            args.clearing = True
        elif args.preset == 'tpers':
            args.agg = True
            args.interact = True
        elif args.preset == 'reps':
            args.reps = True
            args.interact = True

    if args.default_frames:
        args.frames = FRAMES[args.dataset][args.file]


    input_data = try_cache(InputData, args)
    pers_data = None

    if args.agg:
        pers_data = load_range(input_data, args)
        if pers_data is None:
            sys.exit(1)

    elif args.nofilt and not args.nopers:
        pers_data = skip_filt(input_data.name, args)
        if pers_data is None:
            args.nofilt = False

    if not args.nofilt and not args.agg:
        filt_data = try_cache(filt_cls(args), args, input_data)

    if not args.nopers:
        if pers_data is None:
            pers_data = try_cache(pers_cls(args), args, filt_data)

        if args.interact or args.show or IPYTHON:
            tpers_data = TPers(pers_data, **get_kwargs(TPers, args))

            if args.interact:
                if args.reps and not args.nofilt:
                    pers_interact = pers_interact_cls(args)(pers_data, filt_data, input_data)
                    tpers_interact = TPersInteract(tpers_data, pers_data, pers_interact, args.histo)
                else:
                    tpers_interact = TPersInteractBase(tpers_data, pers_data, args.histo)

            elif args.show:
                tpers_data.plot()
                plt.show(block=False)

            if not IPYTHON:
                input('[ Press any key (in the terminal) to exit ]')
