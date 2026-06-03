import numpy as np

def f(y):
    return np.array([y[1], -y[0]])

yz = np.array([1.0, 0.0])
h = 0.1
for i in range(10):
    k1 = f(yz)
    k2 = f(yz + h/2 * k1)
    k3 = f(yz + h/2 * k2)
    k4 = f(yz + h * k3)
    yz += h/6 * (k1 + k2*2 + k3*2 + k4)
    print(yz)

