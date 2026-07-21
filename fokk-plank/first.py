import matplotlib.pyplot as plt
import numpy as np

D = 0.2
xL, xR = -3, 3
N = 300
T = 8.0
save_every = 20

x = np.linspace(xL, xR, N)
dx = x[1] - x[0]


def a(x):
    return x - x**3


amax = np.max(np.abs(a(x)))
dt_diff = dx**2 / (2 * D)
dt_drift = dx / (amax + 1e-12)
dt = 0.35 * min(dt_diff, dt_drift)

steps = int(T / dt)

m0 = 0
sigma0 = 0.18

P = np.exp(-((x - m0) ** 2) / (2 * sigma0**2))
P = P / (np.sum(P) * dx)

P_history = []
t_history = []

for n in range(steps + 1):
    t = n * dt

    if n % save_every == 0:
        P_history.append(P.copy())
        t_history.append(t)

    J = np.zeros(N + 1)

    for i in range(N - 1):
        x_half = 0.5 * (x[i] + x[i + 1])
        a_half = a(x_half)

        if a_half >= 0:
            P_up = P[i]
        else:
            P_up = P[i + 1]

        drift_flux = a_half * P_up
        diff_flux = -D * (P[i + 1] - P[i]) / dx

        J[i + 1] = drift_flux + diff_flux

    J[0] = 0.0
    J[-1] = 0.0

    P = P - dt / dx * (J[1:] - J[:-1])

    P[P < 0] = 0.0

    P = P / (np.sum(P) * dx)

P_history = np.array(P_history)
t_history = np.array(t_history)

X, T_grid = np.meshgrid(x, t_history)

fig = plt.figure(figsize=(11, 7))
ax = fig.add_subplot(111, projection="3d")

ax.plot_surface(X, T_grid, P_history, cmap="viridis", linewidth=0, antialiased=True)

ax.set_xlabel("x")
ax.set_ylabel("t")
ax.set_zlabel("P(x,t)")
ax.set_title("Плотности")

plt.tight_layout()
fig.savefig("fokk-plank-2.png", dpi=130)
