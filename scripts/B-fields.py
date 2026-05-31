import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm



if __name__ == "__main__":
    root = "../data/" # final / needed
    models = sorted(glob.glob(root+"*.*rot*/"))

    fig = plt.figure(figsize=(8,16))
    gs = gridspec.GridSpec(100, 100)
    ax0 = fig.add_subplot(gs[:50, :])
    ax1 = fig.add_subplot(gs[50:, :])

    for mod in models:
        pfile = mod+"LOGS/CHE_single_core_collapse.data"
        src, col = get_src_col(pfile)
        m = src[:, col.index("mass")]
        Bphi = 10.0**(src[:, col.index("dynamo_log_B_phi")])
        Br = 10.0**(src[:, col.index("dynamo_log_B_r")])
        ax0.plot(m, Bphi, c='C0', alpha=0.3, lw=0.5)
        ax1.plot(m, Br, c='C0', alpha=0.3, lw=0.5)
        M, o = get_model_initial_values(mod)
        if M==40 and o==0.99:
            ax0.plot(m, Bphi, lw=3, c='C1', zorder=10)
            ax1.plot(m, Br, lw=3, c='C1', zorder=10)

    ax0.set_ylim(1e4, 1e13)
    ax0.set_yscale('log')
    ax0.set_xscale('log')
    ax0.set_xlim(5e-4, 50)
    ax0.set_xticks([1e-3, 1e-1, 1e1], minor=True)
    ax0.set_xticklabels([], minor=True)
    ax0.set_yticks([1e13, 1e11, 1e9, 1e7, 1e5], minor=True)
    ax0.set_yticklabels([], minor=True)
    ax1.set_ylim(1e4, 1e13)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax1.set_xlim(5e-4, 50)
    ax1.set_xticks([1e-3, 1e-1, 1e1], minor=True)
    ax1.set_xticklabels([], minor=True)
    ax1.set_yticks([1e13, 1e11, 1e9, 1e7, 1e5], minor=True)
    ax1.set_yticklabels([], minor=True)
    ax1.set_xlabel(r"$m\ [M_{\odot}]$")


    ax1.set_xlabel(r"$m\ [M_{\odot}]$")
    ax1.set_ylabel(r"$\log_{10}(B_{r}/\mathrm{[G]})$")
    ax0.set_ylabel(r"$\log_{10}(B_{\varphi}/\mathrm{[G]})$")
    plt.savefig('../manuscript/figures/B_grid.pdf')
