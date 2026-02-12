import cycleflattener
import cycleflattener.utils.exampledata as cue
import matplotlib.pyplot as plt

import pathlib

def generate_slipper(testdata_dir:pathlib.Path,
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

    slipper_dir = testdata_dir / "slipper"
    slipper_dir.mkdir(parents=True, exist_ok=True)

    fname = f"slipper_{r_x}_{r_y}_{r_z}_{back_sole_n}_{front_sole_n}_{front_rise_n}.txt"

    cue.save_data_with_constant_radii(data, 0, slipper_dir / fname)


def main():
    testdata_dir = pathlib.Path(__file__).resolve().parent / "testdata"

    generate_slipper(testdata_dir)
    generate_slipper(testdata_dir,
                     back_sole_n=20,
                     front_sole_n=20,
                     front_rise_n=10)


if __name__ == "__main__":
    main()
