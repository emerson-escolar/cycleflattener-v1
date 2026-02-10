import numpy as np
import pathlib


def generate_soleless_slipper(r_x, r_y, r_z,
                              back_sole_n = 40,
                              front_sole_n = 40,
                              front_rise_n = 15):
    front_limit = np.pi/2

    back_sole_angles = np.linspace(-front_limit, front_limit, back_sole_n)
    front_sole_angles = np.linspace(front_limit, 2*np.pi-front_limit, front_sole_n)
    front_rise_angles = np.linspace(0, np.pi/2, front_rise_n)

    points = []
    for phi in back_sole_angles:
        x = r_x * 1 * np.cos(phi)
        y = r_y * 1 * np.sin(phi)
        z = 0
        points.append([x,y,z])
    for phi in front_sole_angles:
        for theta in front_rise_angles:
            x = r_x * np.sin(theta) * np.cos(phi)
            y = r_y * np.sin(theta) * np.sin(phi)
            z = r_z * np.cos(theta)
            points.append([x,y,z])
    return np.array(points)


def save_data_with_constant_radii(xyz_data:np.array, r:float, fpath:pathlib.Path):
    data = np.concatenate( (xyz_data, np.array([r]*xyz_data.shape[0]).reshape(-1,1)),
                           axis = 1 )
    np.savetxt(fpath, data)
