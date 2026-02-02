import cycleflattener

def main():
    print("Hello from cycleflattener!")
    foo = cycleflattener.filtration.Filtration()

    foo._load_vertices("./testdata/gen_sample_i2p.txt")
    print(foo.vs)

    foo._load_alpha_simplices("./testdata/gen_sample_alphamap.txt")
    print(foo.simplices)

    foo._load_boundary_dict("./testdata/gen_sample_boundary.txt")
    print(foo.boundary_dict)


if __name__ == "__main__":
    main()
