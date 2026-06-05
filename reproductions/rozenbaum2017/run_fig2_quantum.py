"""
Extract quantum CGR from full QKR simulation.
Adaptive kicks (based on t_E) and proper basis.
"""
import numpy as np
from multiprocessing import Pool, cpu_count
from scipy.stats import linregress
import time

HEFF = 2.0**(-14)
SIGMA = 4.0
SAFETY = 2.5

KS_QUANTUM = np.unique(np.sort(np.concatenate([
    np.logspace(-2, 0, 8),    # 0.01-1
    np.linspace(1.2, 5, 10),  # transition
    np.array([6, 8, 10, 15, 20, 30, 50, 100, 300, 1000]),
])))

def gaussian(N, heff, p0, sigma):
    n = np.arange(-N, N)
    psi = np.exp(-(heff*(n-p0/heff))**2/(2*sigma**2))
    return psi / np.sqrt(np.sum(np.abs(psi)**2))

def compute_quantum_cgr(args):
    K, N, heff, n_kicks = args
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

    psi0 = gaussian(N, heff, 0.0, SIGMA)
    phi0 = pop(psi0)
    
    psi_t = [psi0.copy()]
    phi_t = [phi0.copy()]
    psc, phc = psi0.copy(), phi0.copy()
    for _ in range(n_kicks):
        psc = fwd(psc); phc = fwd(phc)
        psi_t.append(psc.copy()); phi_t.append(phc.copy())

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

    # Fit: ln(C(t)) = 2*CGR*(t-1) + const, skipping t=0
    logC = np.log(np.maximum(C[1:], 1e-300))
    t_vals = np.arange(1, len(C))
    slope, _, _, _, _ = linregress(t_vals, logC)
    cgr = slope / 2.0
    
    return K, cgr, C

if __name__ == '__main__':
    tasks = []
    for K in KS_QUANTUM:
        p_rms = K * np.sqrt(10 / 2.0)  # estimate for 10 kicks
        n_need = int(SAFETY * max(p_rms, 2*SIGMA) / HEFF)
        N = int(2**max(15, np.ceil(np.log2(n_need))))
        if N > 2**23:
            N = 2**23  # hard cap at 8M
        
        # Adaptive kicks: enough to reach t_E, but not too many
        if K <= 2:
            n_k = 12
        else:
            tE_est = abs(np.log(HEFF)) / max(np.log(K/2), 0.01)
            n_k = min(max(int(1.5 * tE_est), 5), 12)
        tasks.append((K, N, HEFF, n_k))
    
    n_proc = min(len(tasks), cpu_count())
    print(f"Quantum CGR: {len(tasks)} K values, {n_proc} parallel")
    for K, N, _, nk in tasks:
        print(f"  K={K:8.2f}: N={N:9d}, kicks={nk}", end="")
        if K > 10:
            tE = abs(np.log(HEFF))/max(np.log(K/2),0.01)
            print(f"  tE~{tE:.1f}", end="")
        print()
    
    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(compute_quantum_cgr, tasks)
    
    results.sort(key=lambda x: x[0])
    K_q = np.array([r[0] for r in results])
    CGR_q = np.array([r[1] for r in results])
    
    np.savez('/gpfs/flash/home/sunbin/kick/fig2_quantum.npz',
             K=K_q, CGR_quantum=CGR_q)
    
    for K, cgr, _ in results:
        print(f"  K={K:8.2f}: CGR={cgr:.6f}")
    print(f"Total: {time.time()-t0:.0f}s")
