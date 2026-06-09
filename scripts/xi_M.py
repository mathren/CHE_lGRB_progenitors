import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib as mpl
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm
from make_table_content import compute_profile_quantities


if __name__ == "__main__":
    root = "../data/" # final / needed
    hfiles = sorted(glob.glob(root+"*/LOGS/history.data"))
    models = sorted(glob.glob(root+"*.*/"))

    fig = plt.figure()
    gs = gridspec.GridSpec(150, 110)
    ax = fig.add_subplot(gs[:, :100])
    cax = fig.add_subplot(gs[:, 105:])

    bounds = np.linspace(0.5, 1, 11)-0.001  # for coloring by rotation
    cmap = mpl.colormaps["viridis"].resampled(len(bounds) - 1)   # one color per interval
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N)

    for mod in models:
        pfile = mod+"LOGS/CHE_single_core_collapse.data"
        hfile = mod+"LOGS/history.data"
        src, col = get_src_col(hfile)
        Mfe = src[-1, col.index("fe_core_mass")]
        M, o = get_model_initial_values(mod)
        # select color for all panels
        xi, M4, mu4 = compute_profile_quantities(pfile, M_compact=1.75, s_thresh=4.0)
        p = ax.scatter(M, xi, c=o, s=100, cmap=cmap,
                        norm=norm, zorder=2)

    plt.colorbar(p, cax=cax, format='%.1f')
    ax.set_xlabel(r"$M_{\rm ZAMS} \ [M_{\odot}]$")
    ax.set_ylabel(r"Compactness $\xi_{1.75}$")
    cax.set_ylabel(r"$\omega_{\rm ZAMS}/\omega_{\rm crit}$")

    plt.savefig('../manuscript/figures/xi_M.pdf')
    # for README rendering
    plt.savefig('../manuscript/figures/xi_M.png')
    # plt.show()
