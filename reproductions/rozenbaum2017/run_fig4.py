"""Fig 4: B_tau(K) for multiple tau values."""
import numpy as np
from multiprocessing import Pool, cpu_count
import time

HEFF = 1.0; SIGMA = 4.0; N = 16
TAUS = [30000, 300000, 3000000]
KS = np.logspace(-2, 1, 20)

def compute_btau(args):
    K, tau = args
    M = 2*N; nv = np.arange(-N, N, dtype=np.float64)
    Uk = np.exp(-1j*HEFF*nv**2/2.0)
    xs = 2.0*np.pi*np.arange(M)/M; V_phase = K/HEFF
    psi = np.exp(-(HEFF*nv)**2/(2*SIGMA**2))
    psi /= np.sqrt(np.sum(np.abs(psi)**2))
    phi = (HEFF*nv)*psi.copy()
    B_sum = 0.0
    for t in range(tau + 1):
        B_sum += np.real(np.vdot(psi, (HEFF*nv)*phi))
        px = np.fft.fft(psi, norm='ortho'); px *= np.exp(-1j*V_phase*np.cos(xs))
        psi = np.fft.ifft(px, norm='ortho') * Uk
        px = np.fft.fft(phi, norm='ortho'); px *= np.exp(-1j*V_phase*np.cos(xs))
        phi = np.fft.ifft(px, norm='ortho') * Uk
    return K, tau, B_sum / (tau + 1)

if __name__ == '__main__':
    tasks = [(K, tau) for tau in TAUS for K in KS]
    print(f"Fig 4: {len(tasks)} tasks ({len(KS)} K x {len(TAUS)} tau)")
    t0 = time.time()
    with Pool(min(len(tasks), cpu_count())) as p:
        results = p.map(compute_btau, tasks)

    out = {'KS': KS, 'TAUS': np.array(TAUS)}
    for tau in TAUS:
        B_arr = np.array([r[2] for r in results if r[1]==tau])
        out[f'tau{tau}_B'] = B_arr
        vals = B_arr[[0,5,10,15,-1]]
        print(f"  tau={tau:.0e}: B(K=0.01)={vals[0]:.4f} ... B(K=1)~{vals[2]:.4f} ... B(K=10)={vals[-1]:.4f}")
    np.savez('/gpfs/flash/home/sunbin/kick/fig4_data.npz', **out)
    print(f"Total: {time.time()-t0:.0f}s")
