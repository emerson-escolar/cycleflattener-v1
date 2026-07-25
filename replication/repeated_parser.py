import pathlib
import argparse
import textwrap

import glob
import json

import cycleflattener.utils.saveload as sl

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import sys


def construct_parser() -> argparse.ArgumentParser:
    desc = textwrap.dedent('''\
    Program for parsing repeated angle optimization results.
    ''')

    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("inputdir", type=pathlib.Path,
                        help="path to directory where outputs are stored",
                        default=pathlib.Path.cwd())

    parser.add_argument("--outputdir", "-o", type=pathlib.Path,
                        help="path to directory where outputs are stored",
                        default=None)

    parser.add_argument("--bins", "-b", type=int,
                        help="number of bins for histograms",
                        default=10)

    parser.add_argument('--show', action="store_true",
                        help='Show visualizations')

    return parser



def parse_output(fp):
    data = sl.CyclesFileV2(**json.load(fp))
    n = len(data.cycles[-1].cycle)
    l = data.cycles[-1].length
    k = data.cycles[-1].kappa

    return n,l,k


def plot_histo(data:pd.Series, bins:int, xlabel:str, name:str, outputdir:pathlib.Path, show=False):
    f, ax = plt.subplots(figsize=(12.8, 9.6))
    data.plot.hist(ax=ax, bins=bins)
    plt.xlabel(xlabel)
    spath = outputdir / f"{name}.pdf"
    plt.savefig(spath)

    if show:
        plt.show(block=True)

def write_output(ks, fp):
    print(f"Worst kappa: {max(ks)/np.pi} \\pi", file=fp)
    print(f"Best kappa: {min(ks)/np.pi} \\pi", file=fp)
    print(f"Average kappa: {np.mean(ks)/np.pi} \\pi", file=fp)
    print(f"Stddev kappa: {np.std(ks)/np.pi} \\pi", file=fp)

def main():
    args = construct_parser().parse_args()

    if args.outputdir is None:
        outputdir = args.inputdir
    else:
        outputdir = args.outputdir

    ks = []
    ls = []
    ns = []
    for log in args.inputdir.glob('**/*v2.json'):
        with open(log, "r") as fp:
            n,l,k = parse_output(fp)
            ns.append(n)
            ls.append(l)
            ks.append(k)


    plot_histo((pd.Series(ks) / np.pi), args.bins,
               "total absolute curvature (over pi)", "hist_kappa",
               outputdir, args.show)

    plot_histo(pd.Series(ls), args.bins,
               "cycle lengths", "hist_lengths",
               outputdir, args.show)

    plot_histo(pd.Series(ns), args.bins,
               "cycle sizes (number of 1-simplices)", "hist_sizes",
               outputdir, args.show)

    with open(outputdir/ "kappas.csv", "w") as fp:
        for k in ks:
            fp.write(f"{k / np.pi} \\pi\n")

    with open(outputdir/ "kappas_stats.txt", "w") as fp:
        write_output(ks, fp)

    write_output(ks, sys.stdout)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
