import cycleflattener
import cycleflattener.utils.exampledata as cue
import matplotlib.pyplot as plt

import pathlib

def generate_slipper(testdata_dir:pathlib.Path):
    data = cue.generate_soleless_slipper(2, 1, 1)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(data[:, 0], data[:, 1], data[:, 2], s=1, c="blue")
    ax.set_zlim(-1, 1)

    plt.show()

    slipper_dir = testdata_dir / "slipper"
    slipper_dir.mkdir(parents=True, exist_ok=True)

    cue.save_data_with_constant_radii(data, 0, slipper_dir / "slipper.txt")


def main():
    testdata_dir = pathlib.Path(__file__).resolve().parent / "testdata"

    generate_slipper(testdata_dir)


if __name__ == "__main__":
    main()
