import cycleflattener

def main():
    print("Hello from cycleflattener!")
    foo = cycleflattener.filtration.Filtration()

    foo.load_vertices("./tests/testdata/gen_sample_i2p.txt")
    print(foo.vertex_coordinates)

    foo.load_alpha_simplices("./tests/testdata/gen_sample_alphamap.txt", maxbirth=9)
    print(foo.simplices)

    foo.load_boundaries("./tests/testdata/gen_sample_boundary.txt")
    print(foo.boundaries)

    print(foo.num_vertices)

    print(foo.get_neighborhood_simplexindices([1], eps=4))

    print("dim 0 boundary")

    print(foo.get_simplexindices_satisfying(dim=0))
    print(foo.context_boundary_matrix(0).toarray())
    print(foo.get_simplexindices_satisfying(dim=-11))


    print("\ndim 1 boundary")

    print(foo.get_simplexindices_satisfying(dim=1))
    print(foo.context_boundary_matrix(1).toarray())
    print(foo.get_simplexindices_satisfying(dim=0))

    print("\ndim 2 boundary")

    print(foo.get_simplexindices_satisfying(dim=2))
    print(foo.context_boundary_matrix(2).toarray())
    print(foo.get_simplexindices_satisfying(dim=1))

    print("\n")

    print(foo.context_exterior_angles_matrix().toarray())

    foo.load_1_cycles("./tests/testdata/gen_sample_1.txt")
    print(foo.cycles)

    print("optimization target:")
    foo.print_1_cycle(foo.cycles[-1][0])

    foo.compute_angleoptimal_homologous_cycle(foo.cycles[-1], 100)


if __name__ == "__main__":
    main()
