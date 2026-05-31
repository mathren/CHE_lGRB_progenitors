import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from MESAreader import get_src_col, get_model_initial_values

if __name__ == "__main__":
    root = "../data/" # final / needed
    models = sorted(glob.glob(root+"*.*rot*/"))

    fig = plt.figure()
    gs = gridspec.GridSpec(150, 100)
    ax = fig.add_subplot(gs[:, :])

    for mod in models:
        pfile = mod+"LOGS/CHE_single_core_collapse.data"
        src, col = get_src_col(pfile)
        m = src[:, col.index("mass")]
        ye = src[:, col.index('ye')]
        ax.plot(m, ye, c='C0', alpha=0.3, lw=0.5)

        M, o = get_model_initial_values(mod)
        if M==40 and o==0.6:
            ax.plot(m, ye, lw=3, c='C1', zorder=10)
            try:
                small_net = "../data/SMALL_NET/40_rot0.6_small_net/LOGS1/CHE_single_core_collapse.data"
                src, col = get_src_col(small_net)
                m = src[:, col.index("mass")]
                ye = src[:, col.index('ye')]
                ax.plot(m, ye, c='k', ls='-.', lw=1,
                         zorder=10,
                         label=r"$40\,M_{\odot},\ \frac{\omega_{\rm ZAMS}}{\omega_{\rm crit}}=0.6$"+"\n small network")
                ax.legend(fontsize=20, handletextpad=0.1, frameon=True)
            except:
                print("No small net model")
                print("This model is available at https://zenodo.org/records/11375523")
                print("Download and unpack in ./data/SMALL_NET/")
                pass

# ax.set_xscale('log')
ax.set_xlim(0, 4)
ax.set_ylim(0.44, 0.505)
ax.set_ylabel(r"$Y_e=\sum_j\,X_j Z_j / A_j$")
ax.set_xlabel(r"$m\ [M_{\odot}]$")
plt.savefig('../manuscript/figures/entropy.pdf')
plt.savefig('../manuscript/figures/entropy.png')
