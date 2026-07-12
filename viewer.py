import cycleflattener
import cycleflattener.utils.viewer
import cycleflattener.utils.saveload

import json

import pathlib
import argparse

import textwrap


def construct_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for viewing angle optimization results.

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
                        help="path to directory where original point cloud and cycles are stored",
                        default=pathlib.Path.cwd())
    parser.add_argument("cyclesfile", type=pathlib.Path,
                        help="name of solution cycles file")
    return parser



def main():
    args = construct_parser().parse_args()

    filt = cycleflattener.filtration.Filtration()

    filt.load_vertices(args.inputdir / f"gen_{args.inputname}_i2p.txt")
    filt.load_alpha_simplices(args.inputdir / f"gen_{args.inputname}_alphamap.txt")
    filt.load_boundaries(args.inputdir / f"gen_{args.inputname}_boundary.txt")
    filt.load_1_cycles(args.inputdir / f"gen_{args.inputname}_1.txt")

    with open(args.cyclesfile) as fp:
        data = cycleflattener.utils.saveload.read_solution_cycles_v1(fp)

    cycles = [data.original_cycle, ]
    b = data.original_cycle_birth
    d = data.original_cycle_death
    annots = [f"[{b}, {d})", ]

    for cycle in data.solution_cycles:
        cycles.append(cycle)
        annots.append(f"@ {data.filtration_value}")


    cycleflattener.utils.viewer.plotly_data_and_cycle(filt, (cycles, annots), d)


if __name__ == "__main__":
    main()
