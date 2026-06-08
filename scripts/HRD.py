import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm


if __name__ == "__main__":
    root = "../data/" # final / needed
    models = sorted(glob.glob(root+"*.*rot*/"))

    fig = plt.figure()
    gs = gridspec.GridSpec(2, 2)
    ax = fig.add_subplot(gs[:,:])

    for mod in models:
        hfile = mod+"/LOGS/history.data"
        M, o = get_model_initial_values(mod)
        src, col = get_src_col(hfile)
        logT = src[:, col.index("log_Teff")]
        logL = src[:, col.index("log_L")]
        ax.plot(logT, logL, lw=0.5, alpha=0.3, c='C0')
        if M==40 and o==0.6:
            ax.plot(logT, logL, lw=3, c='C1',zorder=10, label=r"$40\,M_{\odot},\ \frac{\omega_{\rm ZAMS}}{\omega_{\rm crit}}=0.6$"+"\n large network")
    try:
        small_net = "../data/SMALL_NET/40_rot0.6_small_net/LOGS1/history.data"
        src, col = get_src_col(small_net)
        logT = src[:, col.index("log_Teff")]
        logL = src[:, col.index("log_L")]
        ax.plot(logT, logL, lw=1, ls='-.', c='k', zorder=10,
                label=r"$40\,M_{\odot},\ \frac{\omega_{\rm ZAMS}}{\omega_{\rm crit}}=0.6$"+"\n small network")
        ax.legend(fontsize=20, handletextpad=0.1, frameon=True)
    except FileNotFoundError:
        print("No small net model")
        print("This model is available at https://zenodo.org/records/11375523")
        print("Download and unpack in ./data/SMALL_NET/")
        pass

    ax.invert_xaxis()
    ax.set_xlabel(r"$\log_{10}(T_\mathrm{eff}/[K])$")
    ax.set_ylabel(r"$\log_{10}(L/L_\odot)$")

    fig.align_ylabels()
    plt.savefig('../manuscript/figures/HRD.pdf')
    plt.savefig('../manuscript/figures/HRD.png')
