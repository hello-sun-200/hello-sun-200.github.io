import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 10, 'axes.labelsize': 12,
    'legend.fontsize': 8, 'lines.linewidth': 1.6, 'lines.markersize': 5,
    'figure.dpi': 150, 'savefig.dpi': 200,
})

d_cl = np.load('/gpfs/flash/home/sunbin/kick/fig2_classical.npz')
d_q = np.load('/gpfs/flash/home/sunbin/kick/fig2_quantum.npz')

K = d_cl['K']
LE_cl = d_cl['LE_classical']
CGR_cl = d_cl['CGR_classical'] 
LE_chir = d_cl['LE_chirikov']
K_q = d_q['K']
CGR_q = d_q['CGR_quantum']

# Filter quantum data: only keep reliable points (basis large enough)
# For K > 100, N=8M cap makes results unreliable
q_ok = K_q <= 100
K_q_ok = K_q[q_ok]
CGR_q_ok = CGR_q[q_ok]
K_q_bad = K_q[~q_ok]
CGR_q_bad = CGR_q[~q_ok]

fig = plt.figure(figsize=(10, 5.5))

# === Main plot (lin-log) ===
ax_main = fig.add_axes([0.13, 0.13, 0.84, 0.83])
ax_main.set_xscale('log')
ax_main.xaxis.set_major_formatter(plt.ScalarFormatter())
ax_main.ticklabel_format(style='plain', axis='x')
ax_main.set_xticks([0.01, 0.1, 1, 10, 100, 1000])
ax_main.set_xticklabels(['0.01', '0.1', '1', '10', '100', '1000'])
ax_main.set_xlabel(r'Kicking strength  $K$', fontsize=14)
ax_main.set_ylabel(r'Exponent', fontsize=14)

# Chirikov (black dashed) - behind everything
ax_main.plot(K, LE_chir, 'k--', lw=1.2, dashes=(6,4), alpha=0.8,
             label=r'Chirikov  $\lambda\approx\ln(K/2)$')

# Classical LE (blue triangles) - sparse markers
idx = np.unique(np.geomspace(1, len(K)-1, 25, dtype=int))
ax_main.plot(K[idx], LE_cl[idx], 'b^', ms=7, mfc='none', mew=1.3,
             label=r'Classical LE  $\lambda$')

# Classical CGR (green solid)
ax_main.plot(K, CGR_cl, '-', color='#2ca02c', lw=2.2,
             label=r'Classical CGR  $\tilde{\lambda}$')

# Quantum CGR (red circles) - reliable points
ax_main.plot(K_q_ok, CGR_q_ok, 'o', color='#d62728', ms=8, mfc='none', mew=1.8,
             label=r'Quantum CGR')

# Unreliable points (faded)
if len(K_q_bad) > 0:
    ax_main.plot(K_q_bad, CGR_q_bad, 'o', color='#d62728', ms=6, mfc='none', mew=1.0, alpha=0.3)

ax_main.legend(fontsize=8.5, loc='upper left', frameon=True, edgecolor='#cccccc',
               ncol=1)
ax_main.grid(True, alpha=0.2, linestyle='--')
ax_main.set_xlim(K[0], K[-1])
ax_main.set_ylim(bottom=-0.05)

# === Inset (linear-linear) - placed in gap at top-right where curves diverge ===
# Paper's inset: K=0~20, shows LE vs CGR difference clearly
ax_inset = fig.add_axes([0.24, 0.43, 0.38, 0.35])
m = K <= 11

# sparse triangles for LE
idx_in = np.unique(np.linspace(0, sum(m)-1, 18, dtype=int))
K_in = K[m][idx_in]
LE_in = LE_cl[m][idx_in]
ax_inset.plot(K_in, LE_in, 'b^', ms=6, mfc='none', mew=1.0, lw=0.6)

ax_inset.plot(K[m], CGR_cl[m], '-', color='#2ca02c', lw=1.8)
ax_inset.plot(K[m], LE_chir[m], 'k--', lw=1.0, dashes=(6,4), alpha=0.7)

qm = K_q_ok <= 10
ax_inset.plot(K_q_ok[qm], CGR_q_ok[qm], 'o', color='#d62728', ms=7, mfc='none', mew=1.3)

ax_inset.set_xlabel(r'$K$', fontsize=11)
ax_inset.set_ylabel('Exponent', fontsize=10)
ax_inset.grid(True, alpha=0.15, linestyle='--')
ax_inset.set_xlim(0, 10)

for fmt in ['png', 'pdf']:
    plt.savefig(f'/gpfs/flash/home/sunbin/kick/fig2.{fmt}')
print("Saved fig2.png + fig2.pdf")
