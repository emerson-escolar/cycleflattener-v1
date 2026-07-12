import cycleflattener
import cycleflattener.utils.viewer
import cycleflattener.utils.saveload as sl

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

    parser.add_argument("--lifespan_ratio", "-r", type=float,
                        help="lifespan ratio r. Alpha complex constructed at b+(d-b)*r",
                        default=0.5)

    parser.add_argument("--cplex_config_file", "-c", type=pathlib.Path,
                        help="cplex config file", default=None)

    parser.add_argument("--timelimit", "-t", type=int,
                        help="Sets the maximum time, in seconds, for one call to the optimizer. Overrides value in cplex_config_file",
                        default=None)

    parser.add_argument("--nsolves", "-n", type=int,
                        help="Number of times to call the optimizer.",
                        default=None)

    return parser


def plot_data_and_cycle(filt, cycle, color,
                        ofname:pathlib.Path, show=False):
    #  cycle is a dictionary {simplexindex:coeff} representing a cycle.
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

    relbirth = bd[0] + (bd[1]-bd[0]) * args.lifespan_ratio

    # display optimization target
    print("******************************")
    print("optimization target:")
    filt.print_1_cycle(cycle)
    plot_data_and_cycle(filt, cycle, "red",
                        args.outputdir / f"{args.inputname}_cyclebefore.pdf")
    plt.close()
    print("******************************")

    # details:
    print(f"n0: {filt.num_vertices}")
    print(f"n1: {len(filt.get_simplexindices_satisfying(dim=1,maxbirth=relbirth))}")
    print(f"n2: {len(filt.get_simplexindices_satisfying(dim=2,maxbirth=relbirth))}")
    print(f"||z0||_0: {len(cycle)}")
    print(f"l(z0): {filt.get_1_cycle_geometric_length(cycle)}")
    print(f"[b,d): {bd}")
    print(f"z0: {cycle}")
    print("******************************")

    print(f"r: {relbirth}")

    cycles_v2 = [sl.CycleV2(birth=bd[0],
                            death=bd[1],
                            length=filt.get_1_cycle_geometric_length(cycle),
                            kappa=filt.get_1_cycle_total_absolute_curvature(cycle),
                            cycle=cycle), ]

    # optimize
    soln_cycles, soln_values = filt.context_compute_angleoptimal_homologous_cycle_repeated(filt.cycles[idx], maxbirth=relbirth, qcr_shift=args.shift, export_file=args.outputdir / f"{args.inputname}.lp", cplex_config_file=cf, timelimit=args.timelimit, n_epoch=args.nsolves)

    # report results
    for i, soln_cycle in enumerate(soln_cycles):
        plot_data_and_cycle(filt, soln_cycle, "green",
                            args.outputdir / f"{args.inputname}_cycleafter_{i+1}.pdf")

        print(f"z_{i+1}: computed kappa: {soln_values[i]} and {filt.get_1_cycle_total_absolute_curvature(soln_cycle)}")

        cycle_p = sl.CycleV2(filtration_value=relbirth,
                             length=filt.get_1_cycle_geometric_length(soln_cycle),
                             kappa=soln_values[i],
                             cycle=soln_cycle)
        cycles_v2.append(cycle_p)


    with open(args.outputdir / f"{args.inputname}_solutions.json", "w") as fp:
        sl.save_solution_cycles_v1(bd, cycle, relbirth, soln_cycles, fp)

    with open(args.outputdir / f"{args.inputname}_solutions_v2.json", "w") as fp:
        fp.write(sl.CyclesFileV2(original_cycle_indices=[0,],
                                 cycles=cycles_v2).model_dump_json(indent=2))



if __name__ == "__main__":
    main()
