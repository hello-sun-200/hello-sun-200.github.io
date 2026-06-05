import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 11, 'axes.labelsize': 13,
    'legend.fontsize': 9, 'lines.linewidth': 1.8, 'lines.markersize': 0,
    'figure.dpi': 150, 'savefig.dpi': 200,
})

data = np.load('/gpfs/flash/home/sunbin/kick/fig1_data.npz')
KS = sorted(data['KS'])
n_kicks = int(data.get('n_kicks', 30))

colors = {0.5: '#2166ac', 2.0: '#92c5de', 3.0: '#f4a582',
          6.0: '#d6604d', 10.0: '#b2182b'}

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.5, 7.5), sharex=True)
plt.subplots_adjust(hspace=0.05)

for K in sorted(KS, reverse=True):
    key = f'K{int(K*100):05d}'
    C = data[f'{key}_C']
    B = data[f'{key}_B']
    t = np.arange(len(C))
    c = colors.get(K, 'black')
    ax1.semilogy(t[1:], C[1:], '-', color=c, lw=2.0, label=f'$K={K}$')
    ax2.plot(t, B, '-', color=c, lw=2.0, label=f'$K={K}$')

ax1.set_ylabel(r'$C(t)$', fontsize=15)
ax1.legend(fontsize=9, ncol=2, loc='upper left', frameon=True, edgecolor='#ccc')
ax1.grid(True, alpha=0.2, linestyle='--')
ax1.set_xlim(0, n_kicks)
ax1.tick_params(labelbottom=False)

ax2.set_xlabel(r'Number of kicks  $t$', fontsize=15)
ax2.set_ylabel(r'$B(t)$', fontsize=15)
ax2.legend(fontsize=9, ncol=2, loc='best', frameon=True, edgecolor='#ccc')
ax2.grid(True, alpha=0.2, linestyle='--')

plt.savefig('/gpfs/flash/home/sunbin/kick/fig1.png')
plt.savefig('/gpfs/flash/home/sunbin/kick/fig1.pdf')
print("Saved fig1 (no titles, tight)")
