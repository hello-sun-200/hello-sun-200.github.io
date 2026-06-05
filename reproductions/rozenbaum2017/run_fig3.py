"""
Fig 3: ln[C(t)]/2t vs t log-log.
Main: K=3,4,7,10 at heff=2^-14.
Inset: K=4 at heff=2^-14, 2^-10, 2^-6, 2^-2.
Reuses existing Fig1 data for K=3,10.
"""
import numpy as np
from multiprocessing import Pool, cpu_count
import time

SIGMA = 4.0; P0 = 0.0; N_KICKS = 100; SAFETY = 2.5

def gaussian(N, heff, p0, sigma):
    n = np.arange(-N, N)
    psi = np.exp(-(heff*(n-p0/heff))**2/(2*sigma**2))
    return psi / np.sqrt(np.sum(np.abs(psi)**2))

def compute_one(args):
    K, heff, N, n_kicks = args
    nv = np.arange(-N, N, dtype=np.float64)
    Uk = np.exp(-1j*heff*nv**2/2.0)
    Uk_inv = np.exp(1j*heff*nv**2/2.0)
    xs = 2.0*np.pi*np.arange(2*N)/(2*N)
    V_phase = K/heff

    def fwd(psi):
        px = np.fft.fft(psi, norm='ortho')
        px *= np.exp(-1j*V_phase*np.cos(xs))
        return np.fft.ifft(px, norm='ortho') * Uk

    def bwd(psi):
        px = np.fft.fft(psi * Uk_inv, norm='ortho')
        px *= np.exp(1j*V_phase*np.cos(xs))
        return np.fft.ifft(px, norm='ortho')

    def pop(psi):
        return (heff * nv) * psi

    psi0 = gaussian(N, heff, P0, SIGMA)
    phi0 = pop(psi0)

    psi_t = [psi0.copy()]; phi_t = [phi0.copy()]
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

    logC_over_2t = np.zeros(n_kicks)
    for t in range(1, n_kicks+1):
        logC_over_2t[t-1] = np.log(max(C[t], 1e-300)) / (2*t)

    return K, heff, C, logC_over_2t

if __name__ == '__main__':
    HEFF_MAIN = 2.0**(-14)
    tasks = []

    for K in [3.0, 4.0, 7.0, 10.0]:
        p_rms = K * np.sqrt(N_KICKS/2.0)
        n_need = int(SAFETY * max(p_rms, 2*SIGMA) / HEFF_MAIN)
        N = int(2**max(15, np.ceil(np.log2(n_need))))
        tasks.append((K, HEFF_MAIN, N, N_KICKS))
        print(f"K={K}, heff=2^-14: N={N}")

    for hpow in [10, 6, 2]:
        heff = 2.0**(-hpow)
        nk = 20
        p_rms = 4.0 * np.sqrt(nk/2.0)
        n_need = int(SAFETY * max(p_rms, 2*SIGMA) / heff)
        N = int(2**max(8, np.ceil(np.log2(n_need))))
        tasks.append((4.0, heff, N, nk))
        print(f"K=4, heff=2^-{hpow}: N={N}, kicks={nk}")

    t0 = time.time()
    with Pool(min(len(tasks), cpu_count())) as p:
        results = p.map(compute_one, tasks)

    fig1 = np.load('/gpfs/flash/home/sunbin/kick/fig1_data.npz')
    C3 = fig1['K00300_C']; C10 = fig1['K01000_C']
    nk3, nk10 = len(C3)-1, len(C10)-1
    logC3 = np.array([np.log(max(C3[t],1e-300))/(2*t) for t in range(1,nk3+1)])
    logC10 = np.array([np.log(max(C10[t],1e-300))/(2*t) for t in range(1,nk10+1)])

    out = {'K3_logC2t': logC3, 'K10_logC2t': logC10}
    for K, heff, C, lc in results:
        if heff == HEFF_MAIN:
            out[f'K{int(K)}_logC2t_h14'] = lc
        else:
            hp = int(round(-np.log2(heff)))
            out[f'K4_logC2t_h{hp}'] = lc
    out['n_kicks'] = N_KICKS
    np.savez('/gpfs/flash/home/sunbin/kick/fig3_data.npz', **out)

    for K, heff, C, lc in results:
        hp = int(round(-np.log2(heff)))
        print(f"K={K}, heff=2^-{hp}: C(1)={C[1]:.6e}, logC/2t(5)={lc[4]:.4f}")
    print(f"Total: {time.time()-t0:.0f}s")
