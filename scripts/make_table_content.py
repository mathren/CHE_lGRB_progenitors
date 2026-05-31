import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from MESAreader import get_src_col, get_model_initial_values, Rsun_cm
from scipy.interpolate import interp1d

def compute_profile_quantities(pfile, M_compact=1.75, s_thresh=4.0):
    """
    Parameters
    ----------
    pfile : str, path to MESA profile
    M_compact : float, mass in Msun for compactness (default 1.75)
    s_thresh : float, entropy threshold in kB NA (default 4)

    Returns
    -------
    xi : compactness at M_compact
    M_below_s : mass [Msun] with entropy <= s_thresh
    drho_dm : density gradient [g/cm3/Msun] at s = s_thresh
    """
    src, col = get_src_col(pfile)

    mass    = src[:, col.index("mass")]      # Msun, enclosed, should be decreasing in MESA
    radius  = src[:, col.index("radius")]    # Rsun
    logrho  = src[:, col.index("logRho")]    # log10(g/cm3)
    entropy = src[:, col.index("entropy")]   # kB/baryon

    rho = 10**logrho

    # Sort by increasing mass (MESA profiles go surface→center)
    idx = np.argsort(mass)
    mass    = mass[idx]
    radius  = radius[idx]
    rho     = rho[idx]
    entropy = entropy[idx]

    # 1. Compactness xi = (M/Msun) / (R(M) / 1000 km)
    # nearest R
    # R_at_M = radius[np.argmin(np.absolute(mass - M_compact))] * Rsun_cm / 1e8
    # interpolate
    R_interp = interp1d(mass, radius * Rsun_cm / 1e8, bounds_error=False)  # R in 1000 km
    R_at_M = R_interp(M_compact)
    xi = M_compact / R_at_M

    # 2. Mass below entropy threshold s <= s_thresh
    mask = entropy <= s_thresh
    M_below_s = mass[mask].max() if mask.any() else 0.0

    # 3. Density gradient at s = s_thresh (d log rho / d m)
    cross = np.where(np.diff(np.sign(entropy - s_thresh)))[0]
    if len(cross) > 0:
        i = cross[0]
        # Interpolate to get M4 and r(s=4) exactly
        frac = (s_thresh - entropy[i]) / (entropy[i+1] - entropy[i])
        M4   = mass[i]   + frac * (mass[i+1]   - mass[i])    # Msun
        r_s4 = radius[i] + frac * (radius[i+1] - radius[i])  # Rsun

        # Delta m: use next grid point above M4
        delta_m = mass[i+1] - M4                              # Msun
        r_M4_dm = radius[i+1]                                 # Rsun at M4 + delta_m

        # Convert radius difference to 1000 km
        delta_r_1000km = (r_M4_dm - r_s4) * Rsun_cm / 1e8  # 1000 km

        mu4 = delta_m / delta_r_1000km   # Msun / 1000 km
    else:
        mu4 = np.nan

    return xi, M_below_s, mu4



if __name__ == "__main__":
    root = "../data/" # final / needed
    models = sorted(glob.glob(root+"*.*/"))

    print("Copy the output below in ../manuscript/table.tex")
    print("")

    Mprev = -99
    for mod in models:
        hfile = mod+"LOGS/history.data"
        src, col = get_src_col(hfile)
        Mfe = src[-1, col.index("fe_core_mass")]
        he4 = src[-1, col.index("surface_he4")]
        c12 = src[-1, col.index("surface_c12")]
        o16 = src[-1, col.index("surface_o16")]
        pfile = mod+"LOGS/CHE_single_core_collapse.data"
        xi, M4, mu4 = compute_profile_quantities(pfile, M_compact=1.75, s_thresh=4.0)
        M, o = get_model_initial_values(mod)
        if M != Mprev:
            print(r"\hline")
            Mprev = M
        print(f"{M:.2f} & {o:.2f} & {xi:.3f} & {Mfe:.2f} & {M4:.2f} & {mu4:.3f} & {he4:.2f} & {c12:.2f} & {o16:.2f}"+r"\\")
