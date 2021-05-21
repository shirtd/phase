import numpy as np
import argparse


parser = argparse.ArgumentParser(prog='tpers')
parser.add_argument('--directory', default='data', help='data directory.')
parser.add_argument('--dataset', default='lennard-jones', help='data set')
parser.add_argument('--file', default='melt.xyz', help='data file')
parser.add_argument('--frames', nargs=2, type=int, default=(30040,30060), help='frames to load')
# parser.add_argument('--frames', nargs=2, type=int, help='frames to load')
parser.add_argument('--cache', default='cache', help='cache directory')
parser.add_argument('--force', nargs='?', default=[], const=['input', 'complex', 'persist'], help='force module cache override')
parser.add_argument('--parallel', action='store_true', help='compute in parallel')
parser.add_argument('--nocomplex', action='store_true', help='do not compute complexes or persistence')
parser.add_argument('--nopers', action='store_true', help='do not compute persistence')
parser.add_argument('--verbose', action='store_true', help='verbose progress bars')
parser.add_argument('--nocache', action='store_true', help='ignore cache')


parser.add_argument('--dim', type=int, default=3, help='max persistence dimension')
parser.add_argument('--thresh', type=float, default=3/8, help='rips persistence threshold multiplier (multiplied by max bounds)')
parser.add_argument('--lim', type=float, default=1/4, help='diagram plot limit multiplier (multiplied by max bounds)')
# parser.add_argument('--rips', action='store_true', help='do rips persistence')
parser.add_argument('--reps', action='store_true', help='compute (co)cycle representatives')
parser.add_argument('--skip', action='store_true', help='skip to cached diagram.')
parser.add_argument('--clearing', action='store_true', help='clearing optimization.')

parser.add_argument('--delta', default=1/8, type=float, help='distance to boundary multiplier (multiplied by max bounds, relative homology)')
# parser.add_argument('--omega', default=0., type=float, help='modulo sub-levelset (relative homology)')

parser.add_argument('--coh', action='store_true', help='do persistent cohomology')
parser.add_argument('--dual', action='store_true', help='do dual voronoi persistence')

parser.add_argument('--show', action='store_true', help='show plot')
parser.add_argument('--interact', action='store_true', help='interactive plot')
parser.add_argument('--histo', choices={'tpers', 'birth', 'death'}, help='histogram value')

parser.add_argument('--pmin', type=float, default=-np.inf, help='minimum total persistence')
parser.add_argument('--pmax', type=float, default=np.inf, help='maximum total persistence')
parser.add_argument('--bmin', type=float, default=-np.inf, help='minimum birth')
parser.add_argument('--bmax', type=float, default=np.inf, help='maximum birth')
parser.add_argument('--dmin', type=float, default=-np.inf, help='minimum death')
parser.add_argument('--dmax', type=float, default=np.inf, help='maximum death')
parser.add_argument('--average', action='store_true', help='average total persistence')
parser.add_argument('--count', action='store_true', help='count persistence')
