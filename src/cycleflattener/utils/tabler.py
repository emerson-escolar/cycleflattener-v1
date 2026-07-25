import cycleflattener.filtration
import cycleflattener.utils.viz
import cycleflattener.utils.saveload as sl

import json

import pathlib
import argparse

import textwrap

import numpy as np


def construct_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for creating latex rows from angle optimization results.

    Assumes that the files
      gen_{dataname}_i2p.txt
      gen_{dataname}_alphamap.txt
      gen_{dataname}_boundary.txt
      gen_{dataname}_1.txt
    are in the same folder as {args.input} and reads them,
    where dataname is the basename of {args.input} with the suffix .txt removed.
    ''')

    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("input", type=pathlib.Path,
                        help="path to .txt file containing original point cloud")
    parser.add_argument("cyclesfile", type=pathlib.Path,
                        help="name of solution cycles file")
    return parser



class Delims:
    def __init__(self):
        self.delim:str=" & "
        self.math_ldelim:str=r"$"
        self.math_rdelim:str=r"$"
        self.float_ldelim:str=r"\num{"
        self.float_rdelim:str=r"}"

    def _f(self, val)->str:
        return f"{self.float_ldelim}{val}{self.float_rdelim}"

    def _m(self, val)->str:
        return f"{self.math_ldelim}{val}{self.math_rdelim}"

    def _ml(self, arr:list)->list:
        return [self._m(s) for s in arr]


def cycle_stats(filt:cycleflattener.filtration.Filtration, cycle:sl.CycleV2):
    n = len(cycle.cycle)
    l = filt.get_1_cycle_geometric_length(cycle.cycle)
    k = filt.get_1_cycle_total_absolute_curvature(cycle.cycle)

    return n, l, k

def cycle_stats_strings(filt:cycleflattener.filtration.Filtration, cycle:sl.CycleV2, i, x:Delims):
    # header = [f"|z_{i}|" , f"\ell(z_{i})", f"\kappa(z_{i})"]
    # header = [x._m(s) for s in header]

    n, l, k = cycle_stats(filt, cycle)
    # tac = f"{x._f(k)} \\approx {x._f(k/np.pi)} \\pi"
    tac = f"{x._f(k/np.pi)} \\pi"
    entries = x._ml([str(n), x._f(l), tac])

    return entries


def initial_row(filt:cycleflattener.filtration.Filtration,
                  initial_cycle:sl.CycleV2, x:Delims):
    # $n_0$ & $[b,d)$ & $|z_0|$ & $\ell(z_0)$ & $\kappa(z_0)$

    n0 = filt.num_vertices
    b = initial_cycle.birth
    d = initial_cycle.death

    strings = x._ml([str(n0), f"[{x._f(b)}, {x._f(d)})"])
    e = cycle_stats_strings(filt, initial_cycle, 0, x)

    strings.extend(e)

    return x.delim.join(strings)


def cycle_row(filt:cycleflattener.filtration.Filtration,
              cycles:list[sl.CycleV2], x:Delims):

    ans = ""
    for i, cycle in enumerate(cycles):
        e = cycle_stats_strings(filt, cycle, i+1, x)

        ans += x.delim
        ans += x.delim.join(e)
        ans += "\n"

    return ans

def size_row(filt:cycleflattener.filtration.Filtration, filtvalue:float, x:Delims):

    n1 = len(filt.get_simplexindices_satisfying(dim=1,maxbirth=filtvalue))
    n2 = len(filt.get_simplexindices_satisfying(dim=2,maxbirth=filtvalue))

    ans = f"& {x._m(n1)} & {x._m(n2)}"
    return ans

def main():
    args = construct_parser().parse_args()

    filt = cycleflattener.filtration.Filtration()

    inp:pathlib.Path = args.input

    assert(inp.is_file())
    dataname = inp.stem
    inputdir = inp.parent

    filt.load_vertices(inputdir / f"gen_{dataname}_i2p.txt")
    filt.load_alpha_simplices(inputdir / f"gen_{dataname}_alphamap.txt")
    filt.load_boundaries(inputdir / f"gen_{dataname}_boundary.txt")
    filt.load_1_cycles(inputdir / f"gen_{dataname}_1.txt")


    x = Delims()

    with open(args.cyclesfile) as fp:
        data = sl.CyclesFileV2(**json.load(fp))
        cycles_p = data.cycles

        print(initial_row(filt, cycles_p[0], x))
        print(size_row(filt, cycles_p[1].filtration_value, x))
        print(cycle_row(filt, cycles_p[1:], x))






if __name__ == "__main__":
    main()
