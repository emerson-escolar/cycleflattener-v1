import cycleflattener.aohcp_main as cfmain
import textwrap
import sys


def main():
    parser = cfmain.construct_base_parser()

    parser.description = textwrap.dedent('''\
    Program for performing angle optimization on the non-simple cycle with longest lifespan.

    Assumes that the files
      gen_{args.inputname}_i2p.txt
      gen_{args.inputname}_alphamap.txt
      gen_{args.inputname}_boundary.txt
      gen_{args.inputname}_1.txt
    are in {args.inputdir} and reads them.
    ''')

    args = parser.parse_args()

    filt = cfmain.load_filtration(args)

    lifespans = filt.get_lifespans()
    sorted_origidx_lifespan = sorted(zip(range(len(lifespans)), lifespans), key=lambda x: x[1], reverse=True)

    for l_ord, idx_lifespan  in enumerate(sorted_origidx_lifespan):
        idx, _ = idx_lifespan
        cycle, bd = filt.cycles[idx]
        if len(list(filt.get_1_cycle_vertices(cycle))) >= 2:
            print(f"Non-simple cycle found as {l_ord}th lifespan, cycle index {idx}")
            break
    else:
        print("No non-simple cycle in given representative cycles list.")
        sys.exit(0)

    cfmain.main_on_lth_cycle(args, filt, l_ord)


if __name__ == "__main__":
    main()
