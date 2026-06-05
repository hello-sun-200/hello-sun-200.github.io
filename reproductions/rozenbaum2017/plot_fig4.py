"""Fig 4: B_tau(K) for multiple tau."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 11, 'axes.labelsize': 13,
    'legend.fontsize': 9, 'lines.linewidth': 1.6,
    'figure.dpi': 150, 'savefig.dpi': 200,
})

d = np.load('/gpfs/flash/home/sunbin/kick/fig4_data.npz')
KS = d['KS']; TAUS = d['TAUS']
colors = ['#2166ac','#d6604d','#4daf4a','#984ea3','#ff7f00','#a65628']

fig, ax = plt.subplots(figsize=(7, 5))

for i, tau in enumerate(TAUS):
    B = d[f'tau{tau}_B']
    pw = int(np.log10(tau))
    ax.semilogx(KS, B, 'o-', ms=4, lw=1.5, color=colors[i%6],
                label=f'$\\tau=3\\times 10^{{{pw}}}$')

ax.axhline(y=0, color='gray', ls=':', alpha=0.4)
ax.set_xlabel('$K$', fontsize=14)
ax.set_ylabel(r'$\bar{B}_\tau$', fontsize=14)
ax.set_ylim(-0.5, 8.5)
ax.set_xlim(0.008, 12)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
ax.set_title(r'Fig 4: $\bar B_\tau(K)$,  $\hbar_{\rm eff}=1$', fontsize=12)
plt.tight_layout()
plt.savefig('/gpfs/flash/home/sunbin/kick/fig4.png')
plt.savefig('/gpfs/flash/home/sunbin/kick/fig4.pdf')
print("Saved fig4 multi-tau")
