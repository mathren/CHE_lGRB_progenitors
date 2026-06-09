import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import matplotlib.colors as mcolors
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm



if __name__ == "__main__":
    root = "../data/" # final / needed
    models = sorted(glob.glob(root+"*.*rot*/"))

    fig = plt.figure(figsize=(8,16))
    gs = gridspec.GridSpec(100, 100)
    ax0 = fig.add_subplot(gs[:50, :])
    ax1 = fig.add_subplot(gs[50:, :])

    # bounds = np.linspace(30, 100, 71)+0.5   # for coloring by mass
    bounds = np.linspace(0.5, 1, 11)-0.001  # for coloring by rotation
    cmap = mpl.colormaps["viridis"].resampled(len(bounds) - 1)   # one color per interval
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)

    for mod in models:
        M, o = get_model_initial_values(mod)
        # select color
        c=cmap(norm(o))
        pfile = mod+"LOGS/CHE_single_core_collapse.data"
        src, col = get_src_col(pfile)
        m = src[:, col.index("mass")]
        Bphi = 10.0**(src[:, col.index("dynamo_log_B_phi")])
        Br = 10.0**(src[:, col.index("dynamo_log_B_r")])
        ax0.plot(m, Bphi, c=c, alpha=0.3, lw=0.5)
        ax1.plot(m, Br, c=c, alpha=0.3, lw=0.5)
        if M==40 and o==0.99:
            ax0.plot(m, Bphi, lw=3, c='C1', zorder=10)
            ax1.plot(m, Br, lw=3, c='C1', zorder=10)
    try:
        small_net = "../data/SMALL_NET/40_rot0.6_small_net/LOGS1/CHE_single_core_collapse.data"
        src, col = get_src_col(small_net)
        m = src[:, col.index("mass")]
        Bphi = 10.0**(src[:, col.index("dynamo_log_B_phi")])
        Br = 10.0**(src[:, col.index("dynamo_log_B_r")])
        ax0.plot(m, Bphi, c='k', ls='-.', lw=1)
        ax1.plot(m, Br, c='k', ls='-.', lw=1)
    except FileNotFoundError:
        print("No small net model")
        print("This model is available at https://zenodo.org/records/11375523")
        print("Download and unpack in ./data/SMALL_NET/")
        pass

    ax0.set_ylim(1e4, 1e13)
    ax0.set_yscale('log')
    ax0.set_xscale('log')
    ax0.set_xlim(1e-2, 50)
    # ax0.set_xticks([1e-3, 1e-1, 1e1], minor=True)
    # ax0.set_xticklabels([], minor=True)
    ax0.set_yticks([1e13, 1e11, 1e9, 1e7, 1e5], minor=True)
    ax0.set_yticklabels([], minor=True)
    ax1.set_ylim(1e4, 1e13)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax1.set_xlim(1e-2, 50)
    # ax1.set_xticks([1e-3, 1e-1, 1e1], minor=True)
    # ax1.set_xticklabels([], minor=True)
    ax1.set_yticks([1e13, 1e11, 1e9, 1e7, 1e5], minor=True)
    ax1.set_yticklabels([], minor=True)
    ax1.set_xlabel(r"$m\ [M_{\odot}]$")


    ax1.set_xlabel(r"$m\ [M_{\odot}]$")
    ax1.set_ylabel(r"$\log_{10}(B_{r}/\mathrm{[G]})$")
    ax0.set_ylabel(r"$\log_{10}(B_{\varphi}/\mathrm{[G]})$")
    plt.savefig('../manuscript/figures/B_grid.pdf')
    plt.savefig('../manuscript/figures/B_grid.png')
    # plt.show()
