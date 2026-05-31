import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm
import matplotlib.colors as mcolors



if __name__ == "__main__":
    models_tried = 11*71   # see ./setup_single_CHE.py

    root = "../data/" # final / needed
    hfiles = sorted(glob.glob(root+"*/LOGS/history.data"))
    models = sorted(glob.glob(root+"*.*/"))

    success = len(models)/models_tried
    print(f"Total grid success rate: {success:.2f}")

    fig = plt.figure()
    gs = gridspec.GridSpec(150, 110)
    ax = fig.add_subplot(gs[:, :])
    omegas = np.linspace(0.5, 0.99, 11)
    masses = np.linspace(30, 100, 36)

    # Build a set of (M, omega) pairs from existing models
    existing = set()
    for mod in models:
        M, o = get_model_initial_values(mod)
        existing.add((round(M,2), round(o,2)))

    for M in masses:
        for o in omegas:
            if (round(M,2), round(o,2)) in existing:
                ax.plot(M, o, marker='$✓$', color='green', markersize=10, linestyle='None')
            else:
                ax.plot(M, o, marker='x', color='red', markersize=8, linestyle='None',
                        markeredgewidth=1.5)

    ax.set_xlabel(r'$M_{\rm ZAMS} \ [M_{\odot}]$')
    ax.set_ylabel(r'$\omega_{\rm ZAMS}/\omega_{\rm crit}$')
    plt.tight_layout()
    plt.savefig('../manuscript/figures/overview_grid.pdf')
    # for README rendering
    plt.savefig('../manuscript/figures/overview_grid.png')
