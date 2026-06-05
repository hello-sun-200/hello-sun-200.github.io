"""
Supplement large-K quantum CGR with sufficient basis.
K=200, 500, 1000. Run sequentially due to memory.
"""
import numpy as np
from scipy.stats import linregress
import time, sys

HEFF = 2.0**(-14)
SIGMA = 4.0
SAFETY = 2.5

def compute_quantum_cgr(K, N, n_kicks):
    print(f"  [K={K}] N={N:,}, kicks={n_kicks}, mem~{2*N*16/1024**3:.1f}GB/vec", flush=True)
    nv = np.arange(-N, N, dtype=np.float64)
    Uk = np.exp(-1j*HEFF*nv**2/2.0)
    Uk_inv = np.exp(1j*HEFF*nv**2/2.0)
    xs = 2.0*np.pi*np.arange(2*N)/(2*N)
    V_phase = K/HEFF

    def fwd(psi):
        px = np.fft.fft(psi, norm='ortho')
        px *= np.exp(-1j*V_phase*np.cos(xs))
        return np.fft.ifft(px, norm='ortho') * Uk

    def bwd(psi):
        px = np.fft.fft(psi * Uk_inv, norm='ortho')
        px *= np.exp(1j*V_phase*np.cos(xs))
        return np.fft.ifft(px, norm='ortho')

    def pop(psi):
        return (HEFF * nv) * psi

    def gaussian():
        n = np.arange(-N, N)
        psi = np.exp(-(HEFF*n)**2/(2*SIGMA**2))
        return psi / np.sqrt(np.sum(np.abs(psi)**2))

    psi0 = gaussian()
    phi0 = pop(psi0)

    psi_t = [psi0.copy()]
    phi_t = [phi0.copy()]
    ps, ph = psi0.copy(), phi0.copy()
    for _ in range(n_kicks):
        ps = fwd(ps); ph = fwd(ph)
        psi_t.append(ps.copy()); phi_t.append(ph.copy())

    b_tilde = [pop(phi_t[t]).copy() for t in range(n_kicks+1)]
    a_tilde = [pop(psi_t[t]).copy() for t in range(n_kicks+1)]

    for k in range(1, n_kicks+1):
        for t in range(k, n_kicks+1):
            b_tilde[t] = bwd(b_tilde[t])
            a_tilde[t] = bwd(a_tilde[t])

    C = np.zeros(n_kicks+1)
    for t in range(n_kicks+1):
        diff = b_tilde[t] - pop(a_tilde[t])
        C[t] = np.real(np.vdot(diff, diff))

    logC = np.log(np.maximum(C[1:], 1e-300))
    slope, _, _, _, _ = linregress(np.arange(1, len(C)), logC)
    return slope / 2.0

if __name__ == '__main__':
    configs = [
        (200, 2**25, 5),     # 33.5M basis, ~5 kicks, ~32GB/vec
        (500, 2**26, 5),     # 67M basis, ~5 kicks, ~64GB/vec
        (1000, 2**26, 5),    # 67M basis, ~5 kicks
    ]

    results = {}
    for K, N, nk in configs:
        t0 = time.time()
        cgr = compute_quantum_cgr(K, N, nk)
        dt = time.time() - t0
        results[K] = cgr
        print(f"  [K={K}] CGR={cgr:.6f}  ({dt:.0f}s)", flush=True)

    # Merge with existing data
    d = np.load('/gpfs/flash/home/sunbin/kick/fig2_quantum.npz')
    K_old = d['K']
    CGR_old = d['CGR_quantum']

    # Remove old unreliable large-K points (>100)
    ok = K_old <= 100
    K_new = np.sort(np.concatenate([K_old[ok], list(results.keys())]))
    CGR_new = np.array([CGR_old[ok][list(K_old[ok]).index(k)] if k in K_old[ok]
                         else results[k] for k in K_new])

    np.savez('/gpfs/flash/home/sunbin/kick/fig2_quantum.npz',
             K=K_new, CGR_quantum=CGR_new)
    print(f"\nSaved: {len(K_new)} points (large-K replaced with proper basis)")
    for k, c in zip(K_new, CGR_new):
        print(f"  K={k:8.1f}: CGR={c:.6f}")
