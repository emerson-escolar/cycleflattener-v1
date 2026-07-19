import cycleflattener
import cycleflattener.utils.exampledata as cue
import matplotlib.pyplot as plt

import sys
import pathlib

import argparse
import textwrap

import numpy as np

import Bio.PDB as pdb



def construct_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for generating test data.
    ''')

    common_parser = argparse.ArgumentParser(add_help = False)
    common_parser.add_argument("--outputdir", "-o", type=pathlib.Path,
                                help="path to directory where to save output",
                                default=pathlib.Path(__file__).resolve().parent / "testdata")
    common_parser.add_argument("--show", action="store_true", help="plot and show data")

    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="type")

    slipper_parser = subparsers.add_parser('slipper', help='Generate soleless slipper', parents=[common_parser])
    slipper_parser.add_argument("--bs", type=int, help="back_sole_n", default=20)
    slipper_parser.add_argument("--fs", type=int, help="front_sole_n", default=20)
    slipper_parser.add_argument("--fr", type=int, help="front_rise_n", default=10)

    circle_parser = subparsers.add_parser('circle', help='Generate noisy circle', parents=[common_parser])
    circle_parser.add_argument("--num", type=int, help="half of total number of points", default=1000)
    circle_parser.add_argument("--epsilon_str", type=str, help="noise epsilon", default="0.2")
    circle_parser.add_argument("--radius_str", type=str, help="radius", default="1.0")

    torus_parser = subparsers.add_parser('torus', help='Generate sample from solid torus', parents=[common_parser])
    torus_parser.add_argument("--num", type=int, help="half of total number of points", default=1000)
    torus_parser.add_argument("--radius_str", type=str, help="Major radius", default="2.0")
    torus_parser.add_argument("--tube_radius_str", type=str, help="Tube radius", default="0.5")

    double_torus_parser = subparsers.add_parser('doubletorus', help='Generate sample from solid double torus', parents=[common_parser])
    double_torus_parser.add_argument("--num", type=int, help="half of total number of points", default=1000)
    double_torus_parser.add_argument("--radius_str", type=str, help="Major radius", default="2.0")
    double_torus_parser.add_argument("--tube_radius_str", type=str, help="Tube radius", default="0.5")

    cylinder_parser = subparsers.add_parser('cylinder', help='Generate cylinder', parents=[common_parser])
    cylinder_parser.add_argument("--num", type=int, help="number of points along surface", default=1000)
    cylinder_parser.add_argument("--height_str", type=str, help="height", default="2.0")
    cylinder_parser.add_argument("--radius_str", type=str, help="radius", default="1.0")
    cylinder_parser.add_argument("--based", action="store_true", help="add additional points along the base boundary. This doubles the number of points.")

    pdb_parser = subparsers.add_parser('pdb', help='Fetch pdb data', parents=[common_parser])
    pdb_parser.add_argument("pdb", type=str, help="pdb code")
    pdb_parser.add_argument("--pdbdir", type=pathlib.Path,
                            help="path to directory where to save pdb files",
                            default=pathlib.Path(__file__).resolve().parent)

    return parser



def generate_pdb_data(outputdir:pathlib.Path,
                      pdb_code:str,
                      local_pdb_dir:pathlib.Path,
                      show=False):
    # if local_pdb_dir is None:
    #     local_pdb_dir=pathlib.Path.cwd()

    pdbl = pdb.PDBList(pdb=str(local_pdb_dir))
    fname = pdbl.retrieve_pdb_file(pdb_code, file_format="mmCif")
    structure = pdb.MMCIFParser().get_structure(pdb_code, fname)

    all_atoms = []
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    all_atoms.append(atom.coord)
    data = np.array(all_atoms)

    return data



def main():
    parser = construct_parser()
    args = parser.parse_args()

    if args.type is None:
        parser.print_help()
        sys.exit(1)

    args.outputdir.mkdir(parents=True, exist_ok=True)

    if args.type == "slipper":
        r_x = 2
        r_y = 1
        r_z = 1
        back_sole_n = args.bs
        front_sole_n = args.fs
        front_rise_n = args.fr

        data = cue.generate_soleless_slipper(r_x, r_y, r_z, back_sole_n, front_sole_n, front_rise_n)
        dataname = f"slipper_{r_x}_{r_y}_{r_z}_{back_sole_n}_{front_sole_n}_{front_rise_n}"

    elif args.type == "circle":
        epsilon_str = args.epsilon_str
        r_str = args.radius_str
        data = cue.generate_noisy_circle(args.num, epsilon=float(epsilon_str), r=float(r_str), based=True)
        dataname = f"noisy_circle_{r_str}_{args.num}_{epsilon_str}"

    elif args.type == "cylinder":
        h_str = args.height_str
        r_str = args.radius_str
        data = cue.generate_cylinder(args.num, h=float(h_str), r=float(r_str), based=args.based)
        dataname = f"cylinder_{'based_' if args.based else ''}{h_str}_{r_str}_{args.num}"

    elif args.type == "torus":
        R_str = args.radius_str
        r_str = args.tube_radius_str
        data = cue.generate_torus(args.num, R=float(R_str), r=float(r_str))
        dataname = f"solid_torus_{R_str}_{r_str}_{args.num}"

    elif args.type == "doubletorus":
        R_str = args.radius_str
        r_str = args.tube_radius_str
        data = cue.generate_double_torus(args.num, R=float(R_str), r=float(r_str))
        dataname = f"solid_doubletorus_{R_str}_{r_str}_{args.num}"

    elif args.type == "pdb":
        data = generate_pdb_data(args.outputdir, pdb_code=args.pdb, local_pdb_dir=args.pdbdir, show=args.show)
        dataname = f"pdb_{args.pdb}"

    else:
        parser.print_help(sys.stderr)


    cue.save_data_with_constant_radii(data, 0, args.outputdir / f"{dataname}.txt")

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(data[:, 0], data[:, 1], data[:, 2], s=1, c="blue")
    ax.set_box_aspect((np.ptp(data[:,0]), np.ptp(data[:,1]), np.ptp(data[:,2])))
    plt.savefig(args.outputdir / f"{dataname}.pdf")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
