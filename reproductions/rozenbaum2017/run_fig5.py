"""
Fig 5: Classical LE in polar coords (theta=x, r=p+16). 2D colormap only.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from numba import njit
from scipy.interpolate import RegularGridInterpolator

K=1.0; N_GRID=200; N_STEPS=400
P_MIN,P_MAX=-16.0,16.0; LE_MIN,LE_MAX=0,0.3

@njit
def smap(x,p,K):
    pn=p+K*np.sin(x); return (x+pn)%(2*np.pi),pn

@njit
def le_at_point(x0,p0,K,ns):
    tan=np.array([0.0,1e-14]); dn=1e-14; ls=0.0; c=0; x,p=x0,p0
    for s in range(ns):
        pn=p+K*np.sin(x); x=(x+pn)%(2*np.pi); p=pn
        cx=np.cos(x); e,xi=tan[0],tan[1]
        en=e+K*cx*xi; tan=np.array([en,xi+en])
        nd=np.sqrt(tan[0]**2+tan[1]**2)
        if nd>1e-12 and s>10: ls+=np.log(nd/dn); c+=1; tan/=nd; dn=1.0
    return ls/c if c>0 else 0.0

print(f"Computing LE, K={K}...")
xs=np.linspace(0,2*np.pi,N_GRID); ps=np.linspace(P_MIN,P_MAX,N_GRID)
lam=np.zeros((N_GRID,N_GRID))
for i,x0 in enumerate(xs):
    for j,p0 in enumerate(ps): lam[j,i]=le_at_point(x0,p0,K,N_STEPS)
    if i%50==0: print(f"  {i}/{N_GRID}")

NR,NTH=300,600
rs=np.linspace(0,P_MAX-P_MIN,NR)
ths=np.linspace(0,2*np.pi,NTH)
RR,TTH=np.meshgrid(rs,ths)
XX=RR*np.cos(TTH); YY=RR*np.sin(TTH)

le_int=RegularGridInterpolator((ps,xs),lam,bounds_error=False,fill_value=0.0)
lam_polar=le_int(np.column_stack([P_MIN+RR.flatten(),TTH.flatten()])).reshape(NTH,NR)

fig,ax=plt.subplots(figsize=(8,8))
ax.grid(False); ax.set_xticks([]); ax.set_yticks([])

c=ax.pcolormesh(XX,YY,lam_polar,cmap=cm.viridis,shading='gouraud',vmin=LE_MIN,vmax=LE_MAX)
cb=fig.colorbar(c,ax=ax,shrink=0.7,pad=0.04)
cb.set_label(r'$\lambda(x,p)$',fontsize=13)

# x-axis line with labels
Rmax=P_MAX-P_MIN
ax.plot([-Rmax,Rmax],[0,0],'k-',lw=1.0)
ax.plot([0,0],[-Rmax,Rmax],'k-',lw=1.0)
ax.text(-Rmax,0.5,r'$-\pi$',ha='center',fontsize=11)
ax.text(Rmax,0.5,'$0$',ha='center',fontsize=11)
ax.text(1,Rmax,r'$\pi/2$',ha='center',fontsize=9)
ax.text(1,-Rmax,r'$-\pi/2$',ha='center',fontsize=10)

for rpos,lbl,side in [(0,r'$p{=}{-}16$',-1),(16,r'$p{=}0$',1),(32,r'$p{=}16$',-1)]:
    dy=side*2.5
    ax.plot([rpos,rpos],[0,dy],'gray',lw=0.8)
    ax.text(rpos,dy+side*2.5,lbl,fontsize=9,ha='center')

ax.set_aspect('equal')
ax.set_title(r'Classical LE $\lambda(x,p)$, $K{=}1$, polar ($\theta{=}x$, $r{=}p{+}16$)',fontsize=13)
plt.tight_layout()
plt.savefig('/gpfs/flash/home/sunbin/kick/fig5.png',dpi=150)
plt.savefig('/gpfs/flash/home/sunbin/kick/fig5.pdf')
print("Saved fig5")
