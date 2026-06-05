"""
Fig 1: C(t), B(t), 30 kicks, heff=2^-14.
3x safety margin, adaptive ensemble count, max parallelism.
"""
import numpy as np
from multiprocessing import Pool, cpu_count
import time

HEFF = 2.0**(-14)
SIGMA = 4.0
N_KICKS = 30
SAFETY = 3.0

def gaussian(N, heff, p0, sigma):
    n = np.arange(-N, N)
    psi = np.exp(-(heff*(n-p0/heff))**2/(2*sigma**2))
    return psi / np.sqrt(np.sum(np.abs(psi)**2))

def compute_one(args):
    K, N, heff, n_kicks, seed = args
    np.random.seed(seed)
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

    p0 = np.random.uniform(-0.05, 0.05)
    psi0 = gaussian(N, heff, p0, SIGMA)
    phi0 = pop(psi0)

    psi_t = [psi0.copy()]
    phi_t = [phi0.copy()]
    psc, phc = psi0.copy(), phi0.copy()
    for _ in range(n_kicks):
        psc = fwd(psc); phc = fwd(phc)
        psi_t.append(psc.copy()); phi_t.append(phc.copy())

    # Check boundary periodically
    edge = 0.0
    for step in [n_kicks//3, 2*n_kicks//3, n_kicks]:
        e = np.sum(np.abs(psi_t[step][:200])**2) + np.sum(np.abs(psi_t[step][-200:])**2)
        edge = max(edge, e)
    if edge > 1e-3:
        print(f"  !! K={K} edge={edge:.6f} at kick {n_kicks}", flush=True)

    B = np.zeros(n_kicks+1)
    for t in range(n_kicks+1):
        B[t] = np.real(np.vdot(psi_t[t], pop(phi_t[t])))

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

    return K, C, B, edge

if __name__ == '__main__':
    KS = [0.5, 2.0, 3.0, 6.0, 10.0]
    # N_ENS per K: fewer for large N to save memory/time
    ens_config = {0.5: 5, 2.0: 5, 3.0: 4, 6.0: 3, 10.0: 2}

    tasks = []
    N_map = {}
    for K in KS:
        p_rms = K * np.sqrt(N_KICKS / 2.0)
        n_need = int(SAFETY * max(p_rms, 2*SIGMA) / HEFF)
        N = int(2**max(15, np.ceil(np.log2(n_need))))
        N_map[K] = N
        for ie in range(ens_config[K]):
            tasks.append((K, N, HEFF, N_KICKS, ie*1000+int(K*100)))

    n_proc = min(len(tasks), cpu_count())
    print(f"Tasks: {len(tasks)}, parallel: {n_proc}, kicks: {N_KICKS}")
    for K in KS:
        n_mem = 2*N_map[K]*16/1024**2
        n_stored = 2*(N_KICKS+1)*3  # psi_t + phi_t + backward copies
        est = n_mem * n_stored / 1024
        print(f"  K={K}: N={N_map[K]} ({n_mem:.0f}MB/vec), {ens_config[K]}ens, est ~{est:.1f}GB/task")

    t0 = time.time()
    with Pool(n_proc) as p:
        results = p.map(compute_one, tasks)

    C_dict = {K: [] for K in KS}
    B_dict = {K: [] for K in KS}
    max_edge = {K: 0.0 for K in KS}
    for K, C, B, edge in results:
        C_dict[K].append(C)
        B_dict[K].append(B)
        max_edge[K] = max(max_edge[K], edge)

    out = {'KS': np.array(KS), 'n_kicks': N_KICKS}
    for K in KS:
        C_all = np.array(C_dict[K])
        B_all = np.array(B_dict[K])
        out[f'K{int(K*100):05d}_C'] = C_all.mean(axis=0)
        out[f'K{int(K*100):05d}_Cstd'] = C_all.std(axis=0)
        out[f'K{int(K*100):05d}_B'] = B_all.mean(axis=0)
        growth = np.log(C_all.mean(axis=0)[-1]/max(C_all.mean(axis=0)[-2],1e-300))/2
        print(f"K={K}: edge_max={max_edge[K]:.2e}, C(30)={C_all.mean(axis=0)[-1]:.4e}"+
              f" +-{C_all.std(axis=0)[-1]:.1e}, B(0→30)={B_all.mean(axis=0)[0]:.3f}→{B_all.mean(axis=0)[-1]:.3f}")

    np.savez('/gpfs/flash/home/sunbin/kick/fig1_data.npz', **out)
    print(f"Total time: {time.time()-t0:.0f}s")
