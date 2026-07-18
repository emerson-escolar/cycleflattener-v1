import numpy as np
import pathlib


def generate_soleless_slipper(r_x, r_y, r_z, back_sole_n, front_sole_n, front_rise_n):
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


def generate_torus(num, R:float, r:float,
                   theta_low=-np.pi, theta_high=np.pi):

    rng = np.random.default_rng()
    r_vec = rng.uniform(0, r, num)
    phi = rng.uniform(0, 2*np.pi, num)
    theta = np.random.uniform(theta_low, theta_high, num)

    data = np.zeros((num, 3))

    data[:,0] = (R + r_vec * np.cos(phi)) * np.cos(theta)
    data[:,1] = (R + r_vec * np.cos(phi)) * np.sin(theta)
    data[:,2] = r_vec * np.sin(phi)

    return data


def generate_double_torus(num, R:float, r:float):
    # essentially put two torii side by side (with overlap.
    # but, we make the shared region sparser.

    gap = np.arccos(R/(R+r))

    shift_right = np.array([[R, 0, 0]])
    shift_left = np.array([[-R, 0, 0]])

    data = np.concat((shift_left + generate_torus(num//8, R, r),
                      shift_left + generate_torus(num*3//8, R, r, theta_low=gap, theta_high=2*np.pi-gap),
                      shift_right + generate_torus(num//8, R, r),
                      shift_right + generate_torus(num*3//8, R, r, theta_low=gap-np.pi, theta_high=np.pi-gap)))

    return data


def generate_noisy_circle(num, epsilon:float, r:float, based:bool=True):
    data = np.zeros((num, 3))
    theta_list = np.linspace(0, 2 * np.pi, num)
    data[:,0] += r * np.cos(theta_list)
    data[:,1] += r * np.sin(theta_list)

    rng = np.random.default_rng()

    if based:
        base = np.copy(data)
        base[:,0:2] += rng.uniform(-epsilon, epsilon, (num, 2))

    data += rng.uniform(-epsilon, epsilon, (num, 3))

    if based:
        data = np.concatenate((data, base))

    return data


def generate_cylinder(num, h, r, based:bool):
    rng = np.random.default_rng()

    data = np.zeros((num, 3))
    theta = rng.uniform(-np.pi, np.pi, num)

    data[:, 0] = r * np.cos(theta)
    data[:, 1] = r * np.sin(theta)
    data[:, 2] = rng.uniform(0, h, num)

    if based:
        base = np.zeros((num, 3))
        theta = rng.uniform(-np.pi, np.pi, num)
        base[:, 0] = r * np.cos(theta)
        base[:, 1] = r * np.sin(theta)
        data = np.concatenate((data, base))

    return data




def save_data_with_constant_radii(xyz_data:np.array, r:float, fpath:pathlib.Path):
    data = np.concatenate( (xyz_data, np.array([r]*xyz_data.shape[0]).reshape(-1,1)),
                           axis = 1 )
    np.savetxt(fpath, data)
