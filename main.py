import cycleflattener

def main():
    print("Hello from cycleflattener!")
    foo = cycleflattener.filtration.Filtration()

    foo._load_vertices("./testdata/gen_sample_i2p.txt")
    print(foo.vertex_coordinates)

    foo._load_alpha_simplices("./testdata/gen_sample_alphamap.txt", maxbirth=9)
    print(foo.simplices)

    foo._load_boundaries("./testdata/gen_sample_boundary.txt")
    print(foo.boundaries)

    print(foo.num_vertices)

    print(foo.get_neighborhood_simplexindices([1], eps=4))

    print("dim 0 boundary")

    print(foo.get_simplexindices_satisfying(dim=0))
    print(foo.get_boundary_matrix(0).toarray())
    print(foo.get_simplexindices_satisfying(dim=-11))


    print("\ndim 1 boundary")

    print(foo.get_simplexindices_satisfying(dim=1))
    print(foo.get_boundary_matrix(1).toarray())
    print(foo.get_simplexindices_satisfying(dim=0))

    print("\ndim 2 boundary")

    print(foo.get_simplexindices_satisfying(dim=2))
    print(foo.get_boundary_matrix(2).toarray())
    print(foo.get_simplexindices_satisfying(dim=1))

    print("\n")

    print(foo.get_exterior_angles_matrix().toarray())

    foo._load_1_cycles("./testdata/gen_sample_1.txt")
    print(foo.cycles)



if __name__ == "__main__":
    main()
