"""Fig 3: log-derivative vs t, log-log. Main + inset."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 10, 'axes.labelsize': 12,
    'legend.fontsize': 8, 'lines.linewidth': 1.6,
    'figure.dpi': 150, 'savefig.dpi': 200,
})

# Main: K=3 (100k) + K=10 (30k from fig1)
d3 = np.load('/gpfs/flash/home/sunbin/kick/fig3_K3_100.npz')
C3 = d3['C']
d1 = np.load('/gpfs/flash/home/sunbin/kick/fig1_data.npz')
C10 = d1['K01000_C']

def log_deriv(C):
    return np.array([(np.log(max(C[t],1e-300))-np.log(max(C[t-1],1e-300)))/2
                     for t in range(2, len(C))])

ld3 = log_deriv(C3); t3 = np.arange(2, len(C3))
ld10 = log_deriv(C10); t10 = np.arange(2, len(C10))

fig = plt.figure(figsize=(7.5, 5.5))
ax = fig.add_axes([0.13, 0.13, 0.84, 0.83])

ax.loglog(t3, ld3, '-', color='#5e4fa2', lw=2.0, label=r'$K=3$')
ax.loglog(t10, ld10, '-', color='#d53e4f', lw=2.0, label=r'$K=10$')

# Guide lines for CGR plateaus
for y, ls in [(1.03, ':'), (2.00, '--')]:
    ax.axhline(y=y, color='gray', lw=0.8, ls=ls, alpha=0.5)

ax.set_xlabel(r'$t$', fontsize=14)
ax.set_ylabel(r'$[\ln C(t) - \ln C(t-1)]\,/\,2$', fontsize=13)
ax.legend(fontsize=10, loc='lower left', frameon=True, edgecolor='#ccc')
ax.grid(True, alpha=0.2, linestyle='--')
ax.set_xticks([2,3,5,10,20,30,50,100])
ax.set_xticklabels(['2','3','5','10','20','30','50','100'])
ax.set_xlim(2, 100)

plt.savefig('/gpfs/flash/home/sunbin/kick/fig3.png')
plt.savefig('/gpfs/flash/home/sunbin/kick/fig3.pdf')
print("Saved Fig3")
