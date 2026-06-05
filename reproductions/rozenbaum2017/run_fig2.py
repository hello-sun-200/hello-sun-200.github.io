"""
Fig 2: CGR vs LE. FIXED: average eta^2 over trajectories FIRST, then take log ratio.
"""
import numpy as np
from multiprocessing import Pool, cpu_count
from numba import njit
import time

HEFF = 2.0**(-14)
N_GRID = 150; N_STEPS = 400; N_MC = 200000

K_ALL = np.unique(np.sort(np.concatenate([
    np.logspace(-2, 3, 60), np.linspace(0.5, 5, 20)
])))

@njit
def smap(x, p, K):
    pn = p + K*np.sin(x)
    return (x+pn)%(2*np.pi), pn%(2*np.pi)

@njit
def tmap(tan, K, cx):
    e, xi = tan[0], tan[1]
    en = e + K*cx*xi
    return np.array([en, xi+en])

@njit
def le_at_point(x0, p0, K, ns):
    tan = np.array([0.0, 1e-14]); dn = 1e-14; ls = 0.0; c = 0
    x, p = x0, p0
    for s in range(ns):
        x, p = smap(x, p, K)
        tan = tmap(tan, K, np.cos(x))
        nd = np.sqrt(tan[0]**2+tan[1]**2)
        if nd > 1e-12 and s > 10:
            ls += np.log(nd/dn); c += 1
            tan /= nd; dn = 1.0
    return ls/c if c>0 else 0.0

def compute_classical(K):
    xs = np.linspace(0, 2*np.pi, N_GRID)
    ps = np.linspace(0, 2*np.pi, N_GRID)
    lam = np.mean([[le_at_point(x,p,K,N_STEPS) for x in xs] for p in ps])
    
    # Classical CGR: average eta^2 FIRST, then log ratio (correct order!)
    n_fit = min(15, max(3, int(1.0/max(np.log(max(K,1.01)/2), 0.01))))
    eta2_sum = np.zeros(n_fit+1)
    
    for _ in range(N_MC):
        x = np.random.uniform(0, 2*np.pi)
        p = np.random.uniform(0, 2*np.pi)
        tan = np.array([0.0, 1.0])
        x, p = smap(x, p, K)
        tan = tmap(tan, K, np.cos(x))
        eta2_sum[0] += tan[0]**2
        for s in range(1, n_fit+1):
            x, p = smap(x, p, K)
            tan = tmap(tan, K, np.cos(x))
            eta2_sum[s] += tan[0]**2
    
    eta2_avg = eta2_sum / N_MC
    cgr_vals = 0.5 * np.log(np.maximum(eta2_avg[1:], 1e-300) / 
                             np.maximum(eta2_avg[:-1], 1e-300))
    cgr = np.mean(cgr_vals)
    
    def L(xv):
        k = K*np.cos(xv); d = k*(1+k/4)
        if d <= 0: return 1.0
        s = np.sqrt(d)
        return abs(1+k/2 + np.sign(k)*s) if k!=0 else 1.0
    xs_c = np.linspace(-np.pi, np.pi, 40000)
    chir = np.trapezoid(np.log([L(x) for x in xs_c]), xs_c)/(2*np.pi)
    
    return K, lam, cgr, chir

if __name__ == '__main__':
    print(f"Fig2 FIXED: {len(K_ALL)} K values, grid {N_GRID}^2, MC {N_MC}")
    t0 = time.time()
    with Pool(cpu_count()) as p:
        res = p.map(compute_classical, K_ALL)
    res.sort(key=lambda r: r[0])
    K, LE, CGR, CH = [np.array(x) for x in zip(*res)]
    np.savez('/gpfs/flash/home/sunbin/kick/fig2_classical.npz',
             K=K, LE_classical=LE, CGR_classical=CGR, LE_chirikov=CH)
    print(f"Done {time.time()-t0:.0f}s")
    for i in [0, len(K)//4, len(K)//2, 3*len(K)//4, -1]:
        print(f"  K={K[i]:.2f}: LE={LE[i]:.4f} CGR={CGR[i]:.4f} Chir={CH[i]:.4f} diff={CGR[i]-LE[i]:.4f}")
