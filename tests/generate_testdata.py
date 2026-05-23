import cycleflattener
import cycleflattener.utils.exampledata as cue
import matplotlib.pyplot as plt

import pathlib

import argparse
import textwrap



def construct_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for generating test data.
    ''')

    common_parser = argparse.ArgumentParser(add_help = False)

    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    common_parser.add_argument("--outputdir", "-o", type=pathlib.Path,
                                help="path to directory where to save output",
                                default=pathlib.Path(__file__).resolve().parent / "testdata")

    subparsers = parser.add_subparsers(dest="type")

    slipper_parser = subparsers.add_parser('slipper', help='Generate soleless slipper', parents=[common_parser])
    slipper_parser.add_argument("--bs", type=int, help="back_sole_n", default=20)
    slipper_parser.add_argument("--fs", type=int, help="front_sole_n", default=20)
    slipper_parser.add_argument("--fr", type=int, help="front_rise_n", default=10)


    return parser


def generate_slipper(outputdir:pathlib.Path,
                     r_x = 2, r_y = 1, r_z = 1,
                     back_sole_n = 40,
                     front_sole_n = 40,
                     front_rise_n = 15,
                     show=False):
    data = cue.generate_soleless_slipper(r_x, r_y, r_z,
                                         back_sole_n,
                                         front_sole_n,
                                         front_rise_n)

    if show:
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(data[:, 0], data[:, 1], data[:, 2], s=1, c="blue")
        ax.set_zlim(-1, 1)
        plt.show()

    name = f"slipper_{r_x}_{r_y}_{r_z}_{back_sole_n}_{front_sole_n}_{front_rise_n}"
    outputdir.mkdir(parents=True, exist_ok=True)

    fname = f"{name}.txt"
    cue.save_data_with_constant_radii(data, 0, outputdir / fname)


def main():
    args = construct_parser().parse_args()

    generate_slipper(args.outputdir, back_sole_n=args.bs,
                     front_sole_n=args.fs, front_rise_n=args.fr)



if __name__ == "__main__":
    main()
