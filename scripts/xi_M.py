import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm
import matplotlib.colors as mcolors
from make_table_content import compute_profile_quantities


if __name__ == "__main__":
    root = "../data/" # final / needed
    hfiles = sorted(glob.glob(root+"*/LOGS/history.data"))
    models = sorted(glob.glob(root+"*.*/"))

    fig = plt.figure()
    gs = gridspec.GridSpec(150, 110)
    ax = fig.add_subplot(gs[:, :100])
    cax = fig.add_subplot(gs[:, 105:])

    n_colors = 9
    vmin, vmax = 0.55, 1.0

    base_cmap = plt.cm.viridis
    bounds = np.linspace(vmin, vmax, n_colors + 1)
    norm = mcolors.BoundaryNorm(bounds, base_cmap.N)

    cmap_discrete = mcolors.ListedColormap(
        [base_cmap(norm(v)) for v in (bounds[:-1] + bounds[1:]) / 2]
    )
    for mod in models:
        pfile = mod+"LOGS/CHE_single_core_collapse.data"
        hfile = mod+"LOGS/history.data"
        src, col = get_src_col(hfile)
        Mfe = src[-1, col.index("fe_core_mass")]
        M, o = get_model_initial_values(mod)
        xi, M4, mu4 = compute_profile_quantities(pfile, M_compact=1.75, s_thresh=4.0)
        p = ax.scatter(M, xi, c=o, s=100, cmap=cmap_discrete,
                        norm=mcolors.Normalize(vmin, vmax), zorder=2)



    plt.colorbar(p, cax=cax)

    ax.set_xlabel(r"$M_{\rm ZAMS} \ [M_{\odot}]$")
    ax.set_ylabel(r"Compactness $\xi_{1.75}$")
    cax.set_ylabel(r"$\omega_{\rm ZAMS}/\omega_{\rm crit}$")

    plt.savefig('../manuscript/figures/xi_M.pdf')
    # for README rendering
    plt.savefig('../manuscript/figures/xi_M.png')
