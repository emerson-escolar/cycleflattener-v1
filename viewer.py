import cycleflattener
import cycleflattener.utils.viewer
import cycleflattener.utils.saveload as sl

import json

import pathlib
import argparse

import textwrap


def construct_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for viewing angle optimization results.

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
    parser.add_argument("--version", "-r", type=int,
                        help="cycle files veRsion", default=2)
    return parser



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

    if args.version == 1:
        with open(args.cyclesfile) as fp:
            data = sl.CyclesFileV1.model_validate_json(fp.read())

        cycles = [data.original_cycle, ]
        b = data.original_cycle_birth
        d = data.original_cycle_death
        annots = [f"[{b}, {d})", ]

        for cycle in data.solution_cycles:
            cycles.append(cycle)
            annots.append(f"@ {data.filtration_value}")

    elif args.version == 2:
        with open(args.cyclesfile) as fp:
            data = sl.CyclesFileV2(**json.load(fp))
            cycles_p = data.cycles

            b = cycles_p[0].birth
            d = cycles_p[0].death
            annots = [f"orig [{b}, {d}) l={cycles_p[0].length} k={cycles_p[0].kappa}", ]

            for i in range(1, len(cycles_p)):
                annots.append(f"opti @ {cycles_p[i].filtration_value} l={cycles_p[i].length} k={cycles_p[i].kappa}")
            cycles = [x.cycle for x in cycles_p]


    cycleflattener.utils.viewer.plotly_data_and_cycle(filt, (cycles, annots), d)


if __name__ == "__main__":
    main()
