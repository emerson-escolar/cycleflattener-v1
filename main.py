import cycleflattener
import cycleflattener.utils

import numpy as np
import matplotlib.pyplot as plt

import pathlib
import argparse

import textwrap


def construct_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for performing angle optimization on the cycle with the largest lifespan.

    Assumes that the files
      gen_{args.inputname}_i2p.txt
      gen_{args.inputname}_alphamap.txt
      gen_{args.inputname}_boundary.txt
      gen_{args.inputname}_1.txt
    are in {args.inputdir} and reads them.
    ''')

    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("inputname", type=str,
                        help="name in string of data")
    parser.add_argument("--inputdir", "-i", type=pathlib.Path,
                        help="path to directory where inputs are stored",
                        default=pathlib.Path.cwd())

    return parser

def main():
    args = construct_parser().parse_args()

    filt = cycleflattener.filtration.Filtration()

    filt.load_vertices(args.inputdir / f"gen_{args.inputname}_i2p.txt")
    filt.load_alpha_simplices(args.inputdir / f"gen_{args.inputname}_alphamap.txt")
    filt.load_boundaries(args.inputdir / f"gen_{args.inputname}_boundary.txt")
    filt.load_1_cycles(args.inputdir / f"gen_{args.inputname}_1.txt")

    # TODO: change optimization target to cycle with largest lifespan
    lifespans = np.array(filt.get_lifespans())
    idx = np.argmax(lifespans)

    print("optimization target:")
    cycle = filt.cycles[idx][0]
    bd = filt.cycles[idx][1]
    filt.print_1_cycle(cycle)

    filt.context_compute_angleoptimal_homologous_cycle(filt.cycles[idx],
                                                       maxbirth=bd[0])



if __name__ == "__main__":
    main()
