import matplotlib.pyplot as plt
import numpy as np


def rk4step(f, y, h, t=0.0):
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4(f, y0, h=0.1, steps=100, t0=0.0):
    y = np.asarray(y0, dtype=float)
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
    known = np.asarray(known, dtype=float)
    target = np.asarray(target, dtype=float)

    n = len(known_id) + len(unk_id)
    m = len(unk_id)
    steps = round((t1 - t0) / h)

    def build_y0(conds):
        y0 = np.zeros(n)
        y0[known_id] = known
        y0[unk_id] = conds
        return y0

    def residual(conds):
        end = rk4(f, build_y0(conds), h=h, steps=steps, t0=t0)[-1]
        return end[target_id] - target

    conds = np.zeros(m)
    while True:
        r = residual(conds)
        if np.linalg.norm(r) < tol:
            break

        delta = 1e-6
        J = np.zeros((m, m))
        for i in range(m):
            cp = conds.copy()
            cp[i] += delta
            J[:, i] = (residual(cp) - r) / delta
        conds = conds - np.linalg.solve(J, r)

    traj = rk4(f, build_y0(conds), h=h, steps=steps, t0=t0)
    t = t0 + np.arange(len(traj)) * h
    return conds, t, traj


def run(name, f, known_id, known, unk_id, target_id, target, t0, t1, h, exact=None):
    conds, t, traj = shoot(
        f, known_id, known, unk_id, target_id, target, t0=t0, t1=t1, h=h
    )
    y = traj[:, 0]
    print(f"[{name}] conds = {conds}")
    if exact is not None:
        y_true = exact(t)
        err = np.max(np.abs(y - y_true))
        print(f"[{name}] max|y - y_true| = {err:.3e}")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        ax1.plot(t, y, label="численное")
        ax1.plot(t, y_true, "-", label="точное")
        ax1.set_title(name)
        ax1.set_ylabel("y(t)")
        ax1.legend()
        ax1.grid(True)

        ax2.plot(t, y - y_true, color="C3")
        ax2.set_xlabel("t")
        ax2.set_ylabel("y - y_true")
        ax2.grid(True)
    else:
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(t, y, lw=2)
        ax1.set_title(name)
        ax1.set_xlabel("t")
        ax1.set_ylabel("y(t)")
        ax1.grid(True)

    fig.tight_layout()
    fname = f"{name}.png"
    fig.savefig(fname, dpi=120)
    plt.close(fig)
    print(f"[{name}] сохранено -> {fname}")
    return conds, t, traj


def f_ex1(t, y):
    f = 24.0 - (t**2 * (1 - t) ** 2) ** 2
    return np.array([y[1], y[2], y[3], y[0] ** 2 + f])


run(
    "example1_order4",
    f_ex1,
    known_id=[0, 1],
    known=[0, 0],
    unk_id=[2, 3],
    target_id=[0, 1],
    target=[0, 0],
    t0=0.0,
    t1=1.0,
    h=0.001,
    exact=lambda t: t**2 * (1 - t) ** 2,
)


def f_ex2(t, y):
    return np.array([y[1], -y[0]])


run(
    "example2_order2",
    f_ex2,
    known_id=[0],
    known=[0],
    unk_id=[1],
    target_id=[0],
    target=[np.sin(1.5)],
    t0=0.0,
    t1=1.5,
    h=0.001,
    exact=np.sin,
)


def f_ex3(t, y):
    return np.array([y[1], y[2], -y[1]])


run(
    "example3_order3",
    f_ex3,
    known_id=[0],
    known=[0],
    unk_id=[1, 2],
    target_id=[0, 1],
    target=[np.sin(3.0), np.cos(3.0)],
    t0=0.0,
    t1=3.0,
    h=0.001,
    exact=np.sin,
)
