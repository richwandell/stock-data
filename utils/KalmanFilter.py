import numpy as np


class SimpleKalmanFilter:

    def __init__(self, est=1.0, eest=1.0, emea=1.0, kg=0.0, m=1.0):
        self.est = est
        self.eest = eest
        self.emea = emea
        self.kg = kg
        self.m = m

    def update(self, m):
        self.m = m
        self.kg = self.eest / (self.eest + self.emea)
        self.est = self.est + self.kg * (self.m - self.est)
        self.eest = (1 - self.kg) * self.eest
        # self.eest = (self.emea * self.eest) / (self.emea + self.eest)
        return self.est


class KalmanFilter:

    def __init__(self, state_dim=2, measurement_dim=1):
        self.x = np.zeros((state_dim, 1))  # state
        self.P = np.eye(state_dim)  # uncertainty covariance
        self.Q = np.eye(state_dim)  # process uncertainty
        self.B = None  # control transition matrix
        self.F = np.eye(state_dim)  # state transition matrix
        self.H = np.zeros((measurement_dim, state_dim))  # Measurement function
        self.R = np.eye(measurement_dim)  # state uncertainty
        self._alpha_sq = 1.  # fading memory control
        self.M = np.zeros((measurement_dim, measurement_dim))  # process-measurement cross correlation
        self.z = np.array([[None] * measurement_dim]).T

    def add(self, sample):
        self.all_x = sample[0]
        self.all_y = sample[1]
        dv = sample[1] - self.state[1][0]
        A = np.array([
            [1, 1],
            [0, 1]
        ], dtype=float)
        AX = A.dot(self.state)
        B = np.array([
            [0.5],
            [1]
        ])
        u = np.array([[dv / 1]])
        Bu = B*u
        #state matrix
        X = AX+Bu
        x = np.array(self.all_x, dtype=float)
        y = np.array(self.all_y, dtype=float)
        std_x = np.std(x)
        std_y = np.std(y)
        self.state_cov = np.array([
            [0.0, std_x],
            [std_y, 0.0]
        ])

        self.state = X


        # C = np.array([
        #     [p],
        #     [v]
        # ], dtype=float)
        # self.X = C*X