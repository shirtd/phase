import argparse
import numpy as np

parser = argparse.ArgumentParser(prog='tpers')
parser.add_argument('--directory', default='data', help='data directory.')
parser.add_argument('--dataset', default='lennard-jones', help='data set')
parser.add_argument('--file', default='melt.xyz', help='data file')
parser.add_argument('--frames', nargs=2, type=int, default=(30040,30060), help='frames to load')
parser.add_argument('--cache', default='cache', help='cache directory')
parser.add_argument('--force', nargs='?', default=[], const=['input', 'persist'], help='force module cache override')
parser.add_argument('--dim', type=int, default=2, help='max persistence dimension')
parser.add_argument('--thresh', type=float, default=3., help='rips persistence threshold')
parser.add_argument('--lim', type=float, default=1.5, help='diagram plot limit')
parser.add_argument('--rips', action='store_true', help='do rips persistence')
parser.add_argument('--dio', action='store_true', help='use dionysus')
parser.add_argument('--delta', default=1., type=float, help='distance to boundary (relative homology)')
parser.add_argument('--show', action='store_true', help='show plot')
parser.add_argument('--interact', action='store_true', help='interactive plot')


parser.add_argument('--pmin', type=float, default=-np.inf, help='minimum total persistence')
parser.add_argument('--pmax', type=float, default=np.inf, help='maximum total persistence')
parser.add_argument('--average', action='store_true', help='average total persistence')
parser.add_argument('--count', action='store_true', help='count persistence')
