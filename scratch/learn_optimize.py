from typing import List
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt


def objective(x)->float:
    return x[0]+x[1]+x[2]


def constraint(x):
    xsum = sum((x[0], x[1]))
    return xsum - 100.0


b = (0.0, 100.0)
bnds = (b, b, b)
con = {'type': 'eq', 'fun': constraint}

sol = optimize.minimize(
    objective,
    np.array([300.0, 300.0, 300.0]),
    method='SLSQP',
    bounds=bnds,
    constraints=con,
    options={'disp': True}
)

print(sol)

