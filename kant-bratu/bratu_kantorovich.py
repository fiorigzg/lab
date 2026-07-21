import matplotlib.pyplot as plt
import numpy as np

_T = getattr(np, "trapezoid", None) or np.trapz


def rk4step(f, y, h, t=0.0):
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4(f, y0, h=0.1, steps=100, t0=0.0):
    y = np.asarray(y0, float)
    t = t0
    ys = [y.copy()]
    for _ in range(steps):
        y = rk4step(f, y, h, t)
        t += h
        ys.append(y.copy())
    return np.array(ys)


def shoot(
    f, known_id, known, unk_id, target_id, target, t0=0.0, t1=1.0, h=0.001, tol=1e-10
):
    known_id = np.asarray(known_id)
    unk_id = np.asarray(unk_id)
    target_id = np.asarray(target_id)
    known = np.asarray(known, float)
    target = np.asarray(target, float)
    n = len(known_id) + len(unk_id)
    m = len(unk_id)
    steps = round((t1 - t0) / h)

    def build(c):
        y0 = np.zeros(n)
        y0[known_id] = known
        y0[unk_id] = c
        return y0

    def res(c):
        return rk4(f, build(c), h=h, steps=steps, t0=t0)[-1][target_id] - target

    c = np.zeros(m)
    for _ in range(100):
        r = res(c)
        if np.linalg.norm(r) < tol:
            break
        d = 1e-6
        J = np.zeros((m, m))
        for i in range(m):
            cp = c.copy()
            cp[i] += d
            J[:, i] = (res(cp) - r) / d
        c = c - np.linalg.solve(J, r)
    traj = rk4(f, build(c), h=h, steps=steps, t0=t0)
    return c, t0 + np.arange(len(traj)) * h, traj


NY = 400
yg = np.linspace(0.0, 1.0, NY)
g = np.sin(np.pi * yg)
gp = np.pi * np.cos(np.pi * yg)
A = _T(g * g, yg)
B = _T(gp * gp, yg)


def Q(h):
    return _T(g * np.exp(h * g), yg)


def solve_h(lam, step=0.002):
    f = lambda t, s: np.array([s[1], (B * s[0] - lam * Q(s[0])) / A])
    c, x, traj = shoot(f, [0], [0.0], [1], [0], [0.0], t0=0, t1=1, h=step)
    return x, traj[:, 0], c[0]


LAM = 6.0
x, hx, hp0 = solve_h(LAM)
U = np.outer(hx, g)  # u(x,y) = h(x) g(y)
print(f"lambda = {LAM}:  h'(0) = {hp0:.4f},  max u = {U.max():.4f}")

lam_grid, peaks = [], []
for L in np.linspace(0.2, 6.7, 60):
    try:
        _, h, _ = solve_h(L)
        if abs(h[-1]) < 1e-6 and h.max() > 1e-4:
            lam_grid.append(L)
            peaks.append(h.max() * g.max())
    except Exception:
        pass
lam_grid = np.array(lam_grid)
peaks = np.array(peaks)

Xg, Yg = np.meshgrid(x, yg, indexing="ij")
fig = plt.figure(figsize=(10, 8))

ax = fig.add_subplot(1, 1, 1, projection="3d")
xs = x[::8]
Xs, Ys = np.meshgrid(xs, yg[::8], indexing="ij")
Us = np.outer(hx[::8], g[::8])

ax.plot_surface(Xs, Ys, Us, cmap="inferno", linewidth=0, antialiased=True)
ax.set_title("u(x,y)", fontsize=12)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("u")

fig.suptitle(
    rf"Брату, lambda={LAM}",
    fontsize=14,
    y=0.98,
)
fig.tight_layout(rect=[0, 0, 1, 0.95])

fig.savefig("bratu_solution.png", dpi=130)
print("saved bratu_solution.png")
