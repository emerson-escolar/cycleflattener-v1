import cycleflattener.filtration
import cycleflattener.utils.viz as viz
import cycleflattener.utils.saveload as sl

import numpy as np
import matplotlib.pyplot as plt

import pathlib
import argparse

import textwrap


def construct_base_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for performing angle optimization on the cycle associated to the chosen interval.
    The chosen interval is specified by an integer w={args.lifespan_which_ordinal}, which
    means to take the representative cycle of the wth longest interval (where w starts from 0).

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

    parser.add_argument("--outputdir", "-o", type=pathlib.Path,
                        help="path to directory where outputs are stored",
                        default=pathlib.Path.cwd())

    parser.add_argument("--shift", action="store_true", help="shift eigenvalues by 2*pi")

    parser.add_argument("--cplex_config_file", "-c", type=pathlib.Path,
                        help="cplex config file", default=None)

    parser.add_argument("--nolp", action="store_true", help="do not save .lp file")

    parser.add_argument("--timelimit", "-t", type=int,
                        help="Sets the maximum time, in seconds, for one call to the optimizer. Overrides value in cplex_config_file",
                        default=None)

    parser.add_argument("--nsolves", "-n", type=int,
                        help="Number of times to call the optimizer.",
                        default=None)

    parser.add_argument("--lifespan_ratio", "-r", type=float,
                        help="lifespan ratio r. Alpha complex constructed at b+(d-b)*r",
                        default=0.5)

    return parser


def construct_parser() -> argparse.ArgumentParser:
    parser = construct_base_parser()

    parser.add_argument("--lifespan_which_ordinal", "-w", type=int,
                        help="which cycle to work on, specified by ordinal (0th, 1st, 2nd, ...) in lifespans ordered in decreasing order.\
                        Default value of 0 means to take the cycle with longest lifespan.",
                        default=0)

    return parser



def load_filtration(args):
    filt = cycleflattener.filtration.Filtration()

    filt.load_vertices(args.inputdir / f"gen_{args.inputname}_i2p.txt")
    filt.load_alpha_simplices(args.inputdir / f"gen_{args.inputname}_alphamap.txt")
    filt.load_boundaries(args.inputdir / f"gen_{args.inputname}_boundary.txt")
    filt.load_1_cycles(args.inputdir / f"gen_{args.inputname}_1.txt")

    return filt


def prepare_cplex_config(args):
    cf = None
    if args.cplex_config_file is None or args.cplex_config_file.exists():
        cf = [str(args.cplex_config_file), ]
    else:
        print("cplex_config_file ", args.cplex_config_file, " not found. Using defaults.")
    return cf


def print_z0_cycle_details(filt:cycleflattener.filtration.Filtration, cycle, bd:tuple|None):
    print("******************************")
    print("optimization target:")
    print(f"z0: {cycle}")
    print("vertices: ", end="")
    filt.print_1_cycle(cycle)

    print(f"||z0||_0: {len(cycle)}")
    print(f"l(z0): {filt.get_1_cycle_geometric_length(cycle)}")
    print(f"k(z0): {filt.get_1_cycle_total_absolute_curvature(cycle)}")
    if bd is not None:
        print(f"[b,d): {bd}")
    print("******************************")


def print_context(filt, relbirth):
    print("******************************")
    print("optimization context:")
    print(f"r: {relbirth}")
    print(f"n0: {filt.num_vertices}")
    print(f"n1: {len(filt.get_simplexindices_satisfying(dim=1,maxbirth=relbirth))}")
    print(f"n2: {len(filt.get_simplexindices_satisfying(dim=2,maxbirth=relbirth))}")
    print("******************************")


def main():
    args = construct_parser().parse_args()
    filt = load_filtration(args)
    l_ord = args.lifespan_which_ordinal
    main_on_lth_cycle(args, filt, l_ord)


def main_on_lth_cycle(args, filt, l_ord):
    sorted_origidx_lifespan = filt.get_cycleindex_lifespans_nonincreasing()
    idx = sorted_origidx_lifespan[l_ord][0]
    cycle, bd = filt.cycles[idx]
    relbirth = bd[0] + (bd[1]-bd[0]) * args.lifespan_ratio

    main_on_cycle(args, filt, cycle, bd, relbirth, f"{l_ord}th")


def main_on_cycle(args, filt, cycle, bd:tuple|None, relbirth, desc):
    cf = prepare_cplex_config(args)
    args.outputdir.mkdir(exist_ok=True, parents=True)

    print_z0_cycle_details(filt, cycle, bd)
    print_context(filt, relbirth)

    # display optimization target
    viz.plot_data_and_cycle(filt, cycle, "red",
                            args.outputdir / f"{args.inputname}_{desc}_cyclebefore.pdf")
    plt.close()

    cycles_v2 = [sl.CycleV2(birth=None if bd is None else bd[0],
                            death=None if bd is None else bd[1],
                            length=filt.get_1_cycle_geometric_length(cycle),
                            kappa=filt.get_1_cycle_total_absolute_curvature(cycle),
                            cycle=cycle), ]

    export_file = None
    if args.nolp == False:
        export_file=args.outputdir / f"{args.inputname}_{desc}.lp"

    # solve and report results
    i = 0
    for soln_cycle, soln_value in filt.context_solve_aohcp_repeated(cycle, maxbirth=relbirth, qcr_shift=args.shift,
                                                                    export_file=export_file,
                                                                    cplex_config_file=cf, timelimit=args.timelimit, n_epoch=args.nsolves):
        i += 1
        viz.plot_data_and_cycle(filt, soln_cycle, "green",
                                args.outputdir / f"{args.inputname}_{desc}_cycleafter_{i}.pdf")

        print(f"z_{i}: computed kappa: {soln_value} and {filt.get_1_cycle_total_absolute_curvature(soln_cycle)}")

        cycle_p = sl.CycleV2(filtration_value=relbirth,
                             length=filt.get_1_cycle_geometric_length(soln_cycle),
                             kappa=soln_value,
                             cycle=soln_cycle)
        cycles_v2.append(cycle_p)

    with open(args.outputdir / f"{args.inputname}_{desc}_solutions_v2.json", "w") as fp:
        fp.write(sl.CyclesFileV2(original_cycle_indices=[0,],
                                 cycles=cycles_v2).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
