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
    parser.add_argument("--outputdir", "-o", type=pathlib.Path,
                        help="path to directory where outputs are stored",
                        default=pathlib.Path.cwd())
    parser.add_argument("--shift", action="store_true", help="shift eigenvalues by 2*pi")

    parser.add_argument("--cplex_config_file", "-c", type=pathlib.Path,
                        help="cplex config file", default=None)

    parser.add_argument("--timelimit", "-t", type=int,
                        help="Sets the maximum time, in seconds, for a call to an optimizer. Overrides value in cplex_config_file",
                        default=None)

    return parser


def plot_data_and_cycle(filt, cycle, color,
                        ofname:pathlib.Path, show=False):
    data = filt.vertex_coordinates

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(data[:, 0], data[:, 1], data[:, 2], s=1, c="blue")
    for simp_cycle in filt.get_1_cycle_vertices(cycle):
        idxs = simp_cycle + [simp_cycle[0]]
        ax.plot(data[idxs, 0], data[idxs, 1], data[idxs, 2], c=color)

    plt.savefig(ofname)
    if show:
        plt.show(block=True)

def main():
    args = construct_parser().parse_args()

    filt = cycleflattener.filtration.Filtration()

    filt.load_vertices(args.inputdir / f"gen_{args.inputname}_i2p.txt")
    filt.load_alpha_simplices(args.inputdir / f"gen_{args.inputname}_alphamap.txt")
    filt.load_boundaries(args.inputdir / f"gen_{args.inputname}_boundary.txt")
    filt.load_1_cycles(args.inputdir / f"gen_{args.inputname}_1.txt")

    args.outputdir.mkdir(exist_ok=True, parents=True)

    # check cplex config file:
    cf = None
    if args.cplex_config_file.exists():
        cf = [str(args.cplex_config_file), ]
    else:
        print("cplex_config_file ", args.cplex_config_file, " not found. Using defaults.")

    # optimization target is cycle with largest lifespan
    lifespans = np.array(filt.get_lifespans())
    idx = np.argmax(lifespans)
    cycle = filt.cycles[idx][0]
    bd = filt.cycles[idx][1]

    # TODO: setting for at what parameter value to optimize
    # relbirth = bd[0] + (bd[1]-bd[0]) * 0.9999 # just before death
    relbirth = bd[0] # at birth
    relbirth = bd[0] + (bd[1]-bd[0]) * 0.5 # halfway

    # TODO: visualize triangles too
    triangles = filt.context_triangles(relbirth)

    # display optimization target
    print("optimization target:")
    filt.print_1_cycle(cycle)
    plot_data_and_cycle(filt, cycle, "red",
                        args.outputdir / f"{args.inputname}_cyclebefore.pdf")
    plt.close()

    # optimize
    soln_cycles = filt.context_compute_angleoptimal_homologous_cycle_repeated(filt.cycles[idx],
                                                                             maxbirth=relbirth,
                                                                             qcr_shift=args.shift,
                                                                             cplex_config_file=cf,
                                                                             timelimit=args.timelimit,
                                                                             n_epoch=5)

    # report results
    for i, soln_cycle in enumerate(soln_cycles):
        plot_data_and_cycle(filt, soln_cycle, "green",
                            args.outputdir / f"{args.inputname}_cycleafter_{i+1}.pdf")


if __name__ == "__main__":
    main()
