import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm

def my_mark_inset(parent_axes, inset_axes, loc1a=1, loc1b=1, loc2a=2, loc2b=2, **kwargs):
    from mpl_toolkits.axes_grid1.inset_locator import TransformedBbox, BboxPatch, BboxConnector
    rect = TransformedBbox(inset_axes.viewLim, parent_axes.transData)

    pp = BboxPatch(rect, fill=False, **kwargs)
    parent_axes.add_patch(pp)

    p1 = BboxConnector(inset_axes.bbox, rect, loc1=loc1a, loc2=loc1b, **kwargs)
    inset_axes.add_patch(p1)
    p1.set_clip_on(False)
    p2 = BboxConnector(inset_axes.bbox, rect, loc1=loc2a, loc2=loc2b, **kwargs)
    inset_axes.add_patch(p2)
    p2.set_clip_on(False)

    return pp, p1, p2


if __name__ == "__main__":
    root = "../data/" # final / needed
    models = sorted(glob.glob(root+"*.*rot*/"))

    fig = plt.figure(figsize=(15,15))
    gs = gridspec.GridSpec(2, 2)
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[2])
    ax3 = fig.add_subplot(gs[3])
    zx = ax2.inset_axes([0.13, 0.11, 0.68, 0.4])  # for x=logM
    for mod in models:
        hfile = mod+"/LOGS/history.data"
        M, o = get_model_initial_values(mod)

        # HRD ---------------------------------------
        src, col = get_src_col(hfile)
        logT = src[:, col.index("log_Teff")]
        logL = src[:, col.index("log_L")]
        ax0.plot(logT, logL, lw=0.5, alpha=0.3, c='C0')
        if M==40 and o==0.6:
            ax0.plot(logT, logL, lw=3, c='C1',zorder=10)

        # density -----------------------------
        logrho = src[:, col.index("logRho")]
        m = src[:, col.index("mass")]
        ax2.plot(m, logrho, c='C0', alpha=0.3, lw=0.5)
        zx.plot(m, logrho, c='C0', alpha=0.3, lw=0.5)
        if M==40 and o==0.6:
            ax2.plot(m, logrho, lw=3, c='C1', zorder=10)
            zx.plot(m, logrho, lw=3, c='C1', zorder=10)

        # AM profile --------------------------------------------------
        logr = np.log10((10.**(src[:, col.index("logR")]))*Rsun_cm)
        r = 10.0**logr
        omega = src[:, col.index("omega")]
        j_specific = r*r*omega
        m = src[:, col.index("mass")]
        ax3.plot(m, j_specific, c='C0', alpha=0.3, lw=0.5)
        if M==40 and o==0.6:
            ax3.plot(m, j_specific, lw=3, c='C1', zorder=10)

        # Ye ----------------------------------------------------
        pfile = mod+"LOGS/CHE_single_core_collapse.data"
        src, col = get_src_col(pfile)
        m = src[:, col.index("mass")]
        ye = src[:, col.index('ye')]
        ax1.plot(m, ye, c='C0', alpha=0.3, lw=0.5, zorder=1)
        if M==40 and o==0.6:
            ax1.plot(m, ye, lw=3, c='C1', zorder=10, label=r"$40\,M_{\odot},\ \frac{\omega_{\rm ZAMS}}{\omega_{\rm crit}}=0.6$"+"\n large network")
            ax1.axvline(1.75, 0,1,ls='--', lw=2, zorder=9, c='k')
            try:
                small_net = "../data/SMALL_NET/40_rot0.6_small_net/LOGS1/CHE_single_core_collapse.data"
                src, col = get_src_col(small_net)
                m = src[:, col.index("mass")]
                ye = src[:, col.index('ye')]
                ax1.plot(m, ye, c='k', ls='-.', lw=1,
                         zorder=10,
                         label=r"$40\,M_{\odot},\ \frac{\omega_{\rm ZAMS}}{\omega_{\rm crit}}=0.6$"+"\n small network")
                ax1.legend(fontsize=20, handletextpad=0.1, frameon=True)
            except:
                print("No small net model")
                print("This model is available at https://zenodo.org/records/11375523")
                print("Download and unpack in ./data/SMALL_NET/")
                pass



    ax0.invert_xaxis()
    ax0.set_xlabel(r"$\log_{10}(T_\mathrm{eff}/[K])$")
    ax0.set_ylabel(r"$\log_{10}(L/L_\odot)$")

    # ax1.set_xscale('log')
    ax1.set_xlim(0, 4)
    ax1.set_ylim(0.44, 0.505)
    ax1.set_ylabel(r"$Y_e=\sum_j\,X_j Z_j / A_j$")
    ax1.set_xlabel(r"$m\ [M_{\odot}]$")

    ax2.set_ylim(-10, 10.5)
    ax2.set_xscale('log')
    ax2.set_xlim(1e-4, 50)
    zx.set_xlim(1e-4, 5.5)
    zx.set_ylim(2,10)
    ax2.set_xlabel(r"$m\ [M_{\odot}]$")
    ax2.set_ylabel(r"$\log_{10}(\rho/\mathrm{[g\ cm^{-3}}])$")
    my_mark_inset(ax2, zx, loc1a=2, loc1b=3, loc2a=1, loc2b=4)
    ax2.set_xticks([1e-3, 1e-1, 1e1], minor=True)
    ax2.set_xticklabels([], minor=True)

    ax3.set_yscale('log')
    ax3.set_ylim(1e11, 1e19)

    ax3.set_xscale('log')
    ax3.set_xlim(1e-4, 50)
    ax3.set_xticks([1e-3, 1e-1, 1e1], minor=True)
    ax3.set_xticklabels([], minor=True)
    ax3.set_yticks([1e12, 1e14, 1e16, 1e18], minor=True)
    ax3.set_yticklabels([], minor=True)
    ax3.set_xlabel(r"$m\ [M_{\odot}]$")
    # ax3.set_xlabel(r"m [$M_{\odot}$]")
    ax3.set_ylabel(r"$\log_{10}(j/\mathrm{[cm^{2}\ s^{-1}]})$")

    fig.align_ylabels()
    plt.savefig('../manuscript/figures/multipanel_grid.pdf')
    plt.savefig('../manuscript/figures/multipanel_grid.png')
