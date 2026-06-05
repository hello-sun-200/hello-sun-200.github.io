"""
Core module for kicked rotor simulations.
Classical: standard map + tangent map for LE and CGR.
Quantum: Floquet operator evolution + OTOC.
"""
import numpy as np
from numba import njit


# ==============================================================================
# Classical Kicked Rotor
# ==============================================================================

@njit
def standard_map_step(x, p, K):
    """One kick of standard map: p' = p + K*sin(x), x' = x + p' (mod 2pi)."""
    p_new = p + K * np.sin(x)
    x_new = x + p_new
    return x_new % (2 * np.pi), p_new % (2 * np.pi)


@njit
def tangent_map_step(tan_vec, K, cos_x):
    """Apply tangent map to vector (eta, xi) at a point with given cos(x)."""
    eta, xi = tan_vec[0], tan_vec[1]
    eta_new = eta + K * cos_x * xi
    xi_new = xi + eta_new
    return np.array([eta_new, xi_new])


@njit
def iterate_standard_map(x0, p0, K, n_steps):
    """Iterate standard map for n_steps, return trajectory."""
    x, p = x0, p0
    xs = np.empty(n_steps + 1)
    ps = np.empty(n_steps + 1)
    xs[0], ps[0] = x, p
    for i in range(n_steps):
        x, p = standard_map_step(x, p, K)
        xs[i + 1] = x
        ps[i + 1] = p
    return xs, ps


@njit
def compute_lyapunov_at_point(x0, p0, K, n_steps):
    """Compute finite-time Lyapunov exponent at a phase-space point."""
    d0 = 1e-12
    tan = np.array([0.0, d0])  # initial infinitesimal in x-direction
    dist = d0

    d_norm = d0
    lam_sum = 0.0
    x, p = x0, p0
    count = 0

    for step in range(n_steps):
        # evolve standard map
        x, p = standard_map_step(x, p, K)
        # evolve tangent map
        tan = tangent_map_step(tan, K, np.cos(x))
        new_dist = np.sqrt(tan[0]**2 + tan[1]**2)
        if new_dist > 1e-12 and step > 0:
            lam_sum += np.log(new_dist / d_norm)
            count += 1
            # rescale
            tan = tan / new_dist
            d_norm = 1.0

    if count > 0:
        return lam_sum / count
    return 0.0


def compute_lyapunov_phase_space(K, n_steps=500, n_grid=200):
    """Compute LE averaged over phase space grid."""
    xs_grid = np.linspace(0, 2 * np.pi, n_grid)
    ps_grid = np.linspace(0, 2 * np.pi, n_grid)
    lam_map = np.zeros((n_grid, n_grid))

    for i, x0 in enumerate(xs_grid):
        for j, p0 in enumerate(ps_grid):
            lam_map[j, i] = compute_lyapunov_at_point(x0, p0, K, n_steps)

    return xs_grid, ps_grid, lam_map


# ==============================================================================
# Classical CGR (OTOC growth rate)
# ==============================================================================

@njit
def compute_ccl_and_lam(K, n_steps=300, n_grid=200, heff=2**(-14)):
    """
    Compute classical C_cl(t) and Lyapunov exponent by tangent map.
    Returns: avg_lam (scalar LE), ccl (C_cl(t) array), lam_grid (LE per point)
    """
    xs_grid = np.linspace(0, 2 * np.pi, n_grid)
    ps_grid = np.linspace(0, 2 * np.pi, n_grid)
    d0 = 1e-14

    # For C_cl, need Ccl(t) = heff^2 * << (Delta p(t) / Delta x(0))^2 >>
    # Using tangent map: Delta p(t) = eta(t), with xi(0)=1, eta(0)=0
    # Ccl(t) = heff^2 * << eta(t)^2 >> / xi(0)^2 = heff^2 * << eta(t)^2 >>

    ccl_sum = np.zeros(n_steps + 1)
    lam_sum = 0.0
    count = 0
    lam_grid = np.zeros((n_grid, n_grid))

    for i, x0 in enumerate(xs_grid):
        for j, p0 in enumerate(ps_grid):
            x, p = x0, p0
            tan = np.array([0.0, 1.0])  # eta(0)=0, xi(0)=1
            d_norm = 1.0
            lam_local = 0.0
            lam_count = 0

            # Store eta^2 at each step for this trajectory
            eta2_t = np.zeros(n_steps + 1)
            eta2_t[0] = 0.0  # eta(0) = 0

            for step in range(n_steps):
                x, p = standard_map_step(x, p, K)
                tan = tangent_map_step(tan, K, np.cos(x))
                eta2_t[step + 1] = tan[0]**2

                new_dist = np.sqrt(tan[0]**2 + tan[1]**2)
                if new_dist > 1e-12 and step > 0:
                    lam_local += np.log(new_dist / d_norm)
                    lam_count += 1
                    tan = tan / new_dist
                    d_norm = 1.0

            ccl_sum += eta2_t
            if lam_count > 0:
                lam_sum += lam_local / lam_count
                lam_grid[j, i] = lam_local / lam_count
            count += 1

    avg_ccl = heff**2 * ccl_sum / count
    avg_lam = lam_sum / count
    return avg_lam, avg_ccl, lam_grid, xs_grid, ps_grid


def chirikov_lam(K):
    """Chirikov analytical formula for Lyapunov exponent, Eq. (5)-(6)."""
    def L(x_val):
        k = K * np.cos(x_val)
        disc = k * (1 + k / 4)
        if disc < 0:
            return 1.0  # |ell|=1 for oscillatory region
        sqrt_term = np.sqrt(disc)
        if k > 0:
            ell = 1 + k / 2 + sqrt_term
        else:
            ell = 1 + k / 2 - sqrt_term
        return max(abs(ell), 1.0)

    xs = np.linspace(-np.pi, np.pi, 20000)
    L_vals = np.array([L(x) for x in xs])
    return np.trapz(np.log(L_vals), xs) / (2 * np.pi)


# ==============================================================================
# Quantum Kicked Rotor
# ==============================================================================

def build_floquet_ops(N, heff, K):
    """
    Build Floquet operator components.
    F = U_K * U_V
    U_K = exp(-i p^2 / (2 heff))  (kinetic, diagonal in momentum)
    U_V = exp(-i K cos(x) / heff) (potential, diagonal in position)

    Returns functions to apply forward and backward steps.
    """
    n = np.arange(-N, N)
    # Kinetic evolution operator (in momentum basis)
    Uk = np.exp(-1j * heff * n**2 / 2.0)
    Uk_inv = np.exp(1j * heff * n**2 / 2.0)

    def apply_forward(psi):
        """Apply F|psi>."""
        # 1. Potential step in position basis
        psi_x = np.fft.fft(psi, norm='ortho')
        Vx = np.exp(-1j * K * np.cos(2 * np.pi * np.arange(2 * N) / (2 * N)) / heff)
        psi_x = psi_x * Vx
        # 2. Kinetic step in momentum basis
        psi = np.fft.ifft(psi_x, norm='ortho')
        psi = psi * Uk
        return psi

    def apply_backward(psi):
        """Apply F^{-1}|psi>."""
        psi = psi * Uk_inv
        psi_x = np.fft.fft(psi, norm='ortho')
        Vx_inv = np.exp(1j * K * np.cos(2 * np.pi * np.arange(2 * N) / (2 * N)) / heff)
        psi_x = psi_x * Vx_inv
        psi = np.fft.ifft(psi_x, norm='ortho')
        return psi

    def apply_p(psi):
        """Apply p operator in momentum basis: p|n> = heff * n |n>."""
        return heff * n * psi

    def apply_p2(psi):
        """Apply p^2 operator."""
        return (heff * n)**2 * psi

    return apply_forward, apply_backward, apply_p, apply_p2, n


def gaussian_state(N, heff, p0=0.0, sigma=4.0):
    """Create Gaussian wave packet Eq. (4)."""
    n = np.arange(-N, N)
    coeffs = np.exp(-(heff * (n - p0 / heff))**2 / (2 * sigma**2))
    coeffs = coeffs / np.sqrt(np.sum(np.abs(coeffs)**2))
    return coeffs


def compute_otoc_semiclassical(K, n_steps=100, n_traj=50000, heff=2**(-14)):
    """
    Compute OTOC semiclassically:
    C(t) = heff^2 * << (Delta p(t)/Delta x(0))^2 >>
    using Monte Carlo sampling of phase space.
    """
    ccl = np.zeros(n_steps + 1)

    for _ in range(n_traj):
        x = np.random.uniform(0, 2 * np.pi)
        p = np.random.uniform(0, 2 * np.pi)
        tan = np.array([0.0, 1.0])  # eta(0)=0, xi(0)=1

        for step in range(n_steps):
            x, p = standard_map_step(x, p, K)
            tan = tangent_map_step(tan, K, np.cos(x))
            ccl[step + 1] += tan[0]**2

    ccl = heff**2 * ccl / n_traj
    return ccl


def compute_otoc_quantum(N, heff, K, n_steps, p0=0.0, sigma=4.0):
    """
    Full quantum OTOC: C(t) = -<[p(t), p(0)]^2>.

    Uses forward-backward evolution:
    |diff(t)> = F^{-t} p |phi(t)> - p F^{-t} p |psi(t)>
    where |psi(t)> = F^t |psi_0>, |phi(t)> = F^t p|psi_0>.
    """
    fwd, bwd, apply_p, apply_p2, n_vals = build_floquet_ops(N, heff, K)

    psi0 = gaussian_state(N, heff, p0, sigma)
    phi0 = apply_p(psi0)  # p|psi_0>

    # Forward evolve and store all states
    psi_t = [psi0.copy()]
    phi_t = [phi0.copy()]
    psi = psi0.copy()
    phi = phi0.copy()

    for _ in range(n_steps):
        psi = fwd(psi)
        phi = fwd(phi)
        psi_t.append(psi.copy())
        phi_t.append(phi.copy())

    C = np.zeros(n_steps + 1)
    B = np.zeros(n_steps + 1)

    # B(t) = Re <psi_0|p(t) p(0)|psi_0>
    # Compute B(t) efficiently: <psi_0| F^{-t} p F^t p |psi_0>
    # = <psi(t)| p |phi(t)>
    for t in range(n_steps + 1):
        B[t] = np.real(np.dot(np.conj(psi_t[t]), apply_p(phi_t[t])))

    # C(t) via backward evolution
    for t in range(0, n_steps + 1):
        # p|phi(t)>
        p_phi_t = apply_p(phi_t[t])
        # backward evolve: |b_tilde> = F^{-t} p|phi(t)>
        b_tilde = p_phi_t.copy()
        for _ in range(t):
            b_tilde = bwd(b_tilde)

        # p|psi(t)>
        p_psi_t = apply_p(psi_t[t])
        # backward evolve, then apply p
        a_tilde = p_psi_t.copy()
        for _ in range(t):
            a_tilde = bwd(a_tilde)
        p_a_tilde = apply_p(a_tilde)

        # diff = b_tilde - p_a_tilde
        diff = b_tilde - p_a_tilde
        C[t] = np.sum(np.abs(diff)**2)

    return C, B


def compute_otoc_quantum_fast(N, heff, K, n_steps, p0=0.0, sigma=4.0):
    """
    Faster quantum OTOC using the semi-classical identity:
    C(t) = hbar^2 * <(dp(t)/dx(0))^2> evaluated on quantum initial state.

    Uses Wigner-Weyl approach: compute classical trajectories from
    the Wigner distribution of initial state, then compute dp/dx via tangent map.
    """
    # For a Gaussian state with small hbar, this reduces to C_cl(t)
    # computed over the Wigner distribution
    fwd, bwd, apply_p, apply_p2, n_vals = build_floquet_ops(N, heff, K)
    psi0 = gaussian_state(N, heff, p0, sigma)

    # Evolve state forward
    psi_t = [psi0.copy()]
    psi = psi0.copy()
    for _ in range(n_steps):
        psi = fwd(psi)
        psi_t.append(psi.copy())

    # Two-point correlator
    B = np.zeros(n_steps + 1)
    for t in range(n_steps + 1):
        B[t] = np.real(np.dot(np.conj(psi_t[t]), apply_p(psi_t[t])))

    # For OTOC in semiclassical regime, use classical trajectories
    # with initial conditions sampled from Wigner distribution
    n_samples = 10000
    ccl_q = np.zeros(n_steps + 1)

    # Wigner distribution of Gaussian: Gaussian in x and p
    # For psi(x) ~ exp(-heff^2 (n-n0)^2 / (2*sigma^2)), the Wigner function is
    # W(x,p) ~ exp(-(p-p0)^2/sigma^2) * exp(-sigma^2 (x-x0)^2/heff^2)
    # In dimensionless units, sample x uniformly [0,2pi) and p from Gaussian
    sigma_x = heff / (2 * sigma)  # position uncertainty
    sigma_p = sigma  # momentum uncertainty

    for _ in range(n_samples):
        x = np.random.uniform(0, 2 * np.pi)
        p = p0 + sigma_p * np.random.randn()
        # weight by Wigner function... for uniform x sampling, just use p weight
        tan = np.array([0.0, 1.0])

        for step in range(n_steps):
            x, p = standard_map_step(x, p, K)
            tan = tangent_map_step(tan, K, np.cos(x))
            ccl_q[step + 1] += tan[0]**2

    ccl_q = heff**2 * ccl_q / n_samples
    return ccl_q, B


def compute_otoc_small_heff(K, n_steps=100, heff=2**(-14), n_traj=50000):
    """
    For small heff, the quantum OTOC = classical C_cl(t) until Ehrenfest time.
    This function computes C(t) semiclassically with Monte Carlo.
    """
    return compute_otoc_semiclassical(K, n_steps, n_traj, heff)


# ==============================================================================
# Classical Phase Space (for Fig 1 phase portraits)
# ==============================================================================

def generate_phase_portrait(K, n_traj=20, n_steps=500, n_transient=50):
    """Generate phase space portrait by iterating the standard map."""
    xs_points = []
    ps_points = []
    for x0 in np.linspace(0, 2 * np.pi, n_traj):
        for p0 in np.linspace(0, 2 * np.pi, n_traj):
            x, p = x0, p0
            for _ in range(n_transient):
                x, p = standard_map_step(x, p, K)
            for _ in range(n_steps):
                x, p = standard_map_step(x, p, K)
                xs_points.append(x)
                ps_points.append(p)
    return np.array(xs_points), np.array(ps_points)
