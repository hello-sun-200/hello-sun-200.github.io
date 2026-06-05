"""Fig 5: Wigner distribution 3D surface + LE colormap at K=1."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from numba import njit

HEFF = 2.0**(-14); K = 1.0; SIGMA = 4.0
N_GRID = 150; N_STEPS = 300

@njit
def smap(x, p, K):
    pn = p + K*np.sin(x)
    return (x+pn)%(2*np.pi), pn%(2*np.pi)

@njit
def le_at_point(x0, p0, K, ns):
    tan = np.array([0.0, 1e-14]); dn = 1e-14; ls = 0.0; c = 0
    x, p = x0, p0
    for s in range(ns):
        x, p = smap(x, p, K)
        cx = np.cos(x); e, xi = tan[0], tan[1]
        en = e + K*cx*xi; tan = np.array([en, xi+en])
        nd = np.sqrt(tan[0]**2+tan[1]**2)
        if nd > 1e-12 and s > 10: ls += np.log(nd/dn); c += 1; tan /= nd; dn = 1.0
    return ls/c if c>0 else 0.0

print(f"Computing LE grid at K={K}...")
xs_grid = np.linspace(0, 2*np.pi, N_GRID)
ps_grid = np.linspace(0, 2*np.pi, N_GRID)
lam_grid = np.zeros((N_GRID, N_GRID))
for i, x0 in enumerate(xs_grid):
    for j, p0 in enumerate(ps_grid):
        lam_grid[j,i] = le_at_point(x0, p0, K, N_STEPS)
    if i % 30 == 0: print(f"  col {i}/{N_GRID}")

# Wigner distribution on a finer grid for smooth 3D surface
NX, NP = 80, 80
x_wig = np.linspace(0, 2*np.pi, NX)
p_wig = np.linspace(-2*np.pi, 4*np.pi, NP)  # extended p range for visual
XX, PP = np.meshgrid(x_wig, p_wig)
W = np.exp(-PP**2/SIGMA**2) * np.exp(-SIGMA**2 * XX**2/HEFF**2)
W /= W.max()

# Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# LE colormap on the floor (z=-0.05)
Xm, Pm = np.meshgrid(xs_grid, ps_grid)
ax.plot_surface(Xm, Pm, np.full_like(Xm, -0.05),
                facecolors=cm.viridis(lam_grid/lam_grid.max()),
                alpha=0.7, shade=False, antialiased=True)

# Wigner surface
ax.plot_surface(XX, PP, W*0.5, cmap=cm.Reds, alpha=0.8, antialiased=True)

ax.set_xlabel('x'); ax.set_ylabel('p'); ax.set_zlabel('Wigner / LE')
ax.set_title(f'Fig 5: Wigner distribution + LE, K={K}')
ax.set_zlim(-0.05, 0.6)
ax.view_init(elev=25, azim=-60)

plt.tight_layout()
plt.savefig('/gpfs/flash/home/sunbin/kick/fig5.png', dpi=150)
plt.savefig('/gpfs/flash/home/sunbin/kick/fig5.pdf')
print("Saved fig5")
