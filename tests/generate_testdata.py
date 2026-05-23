import cycleflattener
import cycleflattener.utils.exampledata as cue
import matplotlib.pyplot as plt

import sys
import pathlib

import argparse
import textwrap

import numpy as np

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
    circle_parser.add_argument("--epsilon", type=float, help="noise epsilon", default=0.2)
    circle_parser.add_argument("--radius", type=float, help="radius", default=1.0)

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

    outputdir.mkdir(parents=True, exist_ok=True)

    name = f"slipper_{r_x}_{r_y}_{r_z}_{back_sole_n}_{front_sole_n}_{front_rise_n}"
    fname = f"{name}.txt"
    cue.save_data_with_constant_radii(data, 0, outputdir / fname)


def generate_circle(outputdir:pathlib.Path,
                    num, epsilon, r=1,
                    show=False):

    base = np.zeros((num, 3))
    theta_list = np.linspace(0, 2 * np.pi, num)
    base[:,0] += r * np.cos(theta_list)
    base[:,1] += r * np.sin(theta_list)

    data = np.copy(base)
    rng = np.random.default_rng()
    data += rng.uniform(-epsilon, epsilon, (num, 3))

    base[:,0:2] += rng.uniform(-epsilon, epsilon, (num, 2))

    data = np.concatenate((data, base))

    if show:
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(data[:, 0], data[:, 1], data[:, 2], s=1, c="blue")
        ax.set_zlim(-1, 1)
        plt.show()

    outputdir.mkdir(parents=True, exist_ok=True)
    fname = f"noisy_circle_{r}_{num}_{epsilon}.txt"
    cue.save_data_with_constant_radii(data, 0, outputdir / fname)


def main():
    parser = construct_parser()
    args = parser.parse_args()

    if args.type == "slipper":
        generate_slipper(args.outputdir, back_sole_n=args.bs,
                         front_sole_n=args.fs, front_rise_n=args.fr,
                         show=args.show)
    elif args.type == "circle":
        generate_circle(args.outputdir, num=args.num, epsilon=args.epsilon, r=args.radius,
                        show=args.show)
    else:
        parser.print_help(sys.stderr)



if __name__ == "__main__":
    main()
