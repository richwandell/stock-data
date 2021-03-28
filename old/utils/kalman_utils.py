import numpy as np
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import KalmanFilter

DEAD = 99999999999999


def pool_init(queue):
    global q
    q = queue


def kalman(data):
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.x = np.array([
        [data[0][1]],
        [0.0]
    ], dtype=float)
    kf.F = np.array([
        [1., 1.],
        [0., 1.]
    ])
    kf.H = np.array([[1., 0.]])
    kf.P *= 1000.
    kf.R = 5
    kf.Q = Q_discrete_white_noise(2, 1., .1)
    return kf


def run_kalman(input):
    i, future, kalman_data = input

    kf = kalman(kalman_data[0:i])
    for x in kalman_data[1:i]:
        val = np.array([[x[1]]], dtype=float)
        kf.predict()
        kf.update(val)

    for x in range(future):
        kf.predict()

    try:
        val = kalman_data[i+future][1]
        kalman_pd = kalman_data[i+future][2]
        kalman_p = kf.x[0][0]
        error = abs(kf.x[0][0] - val)
        kalman_e = error
        q.put((i, kalman_pd, kalman_p, kalman_e))
    except IndexError as e:
        q.put(DEAD)
