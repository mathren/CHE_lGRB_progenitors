"""
Determine the list of successful models and the success fraction of a grid.

Success criteria for a MESA model:
 - reached `fe_core_infall_limit` termination condition
 - does not exhibit large spikes in L, T_{eff}
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import glob
import sys
import os
import glob
from joblib import Parallel, delayed
from math import pi
from MESAreader import get_src_col, Rsun_cm, Msun, clight, G_cgs, secyer, Lsun
from utilsLib import getTerminationCode
from tqdm import tqdm

def get_L_from_r_teff(radius, teff):
    # to annotate radii on HRD
    # Stephan Boltzman constant
    boltzm = 1.380649e-16  # cgs
    hbar = 6.62607015e-27 / (2 * pi)
    clight = 2.99792458e10
    sigma = (pi * pi * boltzm * boltzm * boltzm * boltzm) / (
        60 * hbar * hbar * hbar * clight * clight
    )
    # convert r to cm
    radius *= Rsun_cm
    # assume teff is in K
    l = 4 * pi * radius * radius * sigma * teff ** 4.0
    # convert to Lsun
    l = l / Lsun
    return l


def annotate_radii_hrd(ax, radii=np.logspace(0, 3, base=10)):
    """
    give the axis object for an HRD plot (assumed to be in log10 Lsun and log10 Teff),
    and a list of radii in Rsun units, plots radii.
    Parameters:
    ----------
    ax: `mpl.ax` matplotlib axis object
    radii: `np.array`, optional, radii to mark
    """
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    Tmax = 10.0 ** xmax
    Tmin = 10.0 ** xmin
    teff = np.linspace(Tmin, Tmax, 10)
    x = np.log10(teff)
    for r in radii:
        l = get_L_from_r_teff(r, teff)
        y = np.log10(l)
        ax.plot(x, y, c="#808080", ls=":", lw=1)
        # ax.text(x[5], y[5], f"{r:.0f}"+r"$\,R_\odot$", fontsize=20,
        # transform=ax.transData, zorder=0, c="#808080"),
        # rotation=np.((max(y)-min(y))/(max(x)-min(x))))
    # reset ylim
    ax.set_ylim(ymin, ymax)


def get_diffs(hfile):
    """
    Calculate differences across timesteps divided final value
    """
    src, col = get_src_col(hfile)
    L = 10.0**(src[:, col.index("log_L")]) # Lsun
    Teff = 10.0**(src[:, col.index("log_Teff")]) # K
    R = src[:, col.index("radius")] # Rsun

    # logt = np.log10(src[:, col.index("star_age")]*secyer)
    # # numpy gradient seems to not have enough precision
    # # returns lots of nans because of tiny timesteps
    # # dL_dt = np.gradient(L, logt) #Lsun/yr
    # # dTeff_dt = np.gradient(Teff, logt) #K/yr
    # # dR_dt = np.gradient(R, logt) #Rsun/yr
    # # add one zero at the end to get same length
    L_frac_dt_var = np.concatenate((np.diff(L)/L[:-1],[0]))
    T_frac_dt_var = np.concatenate((np.diff(Teff)/Teff[:-1],[0]))
    R_frac_dt_var = np.concatenate((np.diff(R)/R[:-1],[0]))
    return (L_frac_dt_var,
            T_frac_dt_var,
            R_frac_dt_var)


def get_delta_HR_div_delta_logR(hfile):
    src, col = get_src_col(hfile)
    logL = src[:, col.index("log_L")]
    logTeff = src[:, col.index("log_Teff")]
    logR = src[:, col.index("log_R")]
    # dt = 10.0**(src[:, col.index("log_dt")])*secyer  # timestep in seconds
    delta_logL = np.diff(logL)
    delta_logTeff = np.diff(logTeff)
    delta_logR = np.diff(logR)
    delta_HR = np.sqrt(delta_logL**2+delta_logTeff**2)
    return delta_HR, delta_logR


# def get_vsurf_div_v_kh(hfile):
#     """ MESA can output this, but we calculate it in post-processing
#     because we didn't save it """
#     src, col = getSrcCol(hfile)
#     v_surf = src[:, col.index("v_surf")]
#     kh_timescale = src[:, col.index("kh_timescale")]*secyer
#     r = 10.**(src[:, col.index("photosphere_log_r")])*Rsun_cm
#     return v_surf/(r/kh_timescale)

def HRD_crossing_out_spikes(model, max_dR = 1e-2, max_dLT = 5e-2, do_plot = True):
    try:
        hfile = model+"/LOGS1/history.data"
        src, col = get_src_col(hfile)
    except FileNotFoundError:
        hfile = model+"/LOGS/history.data"
        src, col = get_src_col(hfile)
    logT = src[:, col.index("log_Teff")]
    logL = src[:, col.index("log_L")]

    # large variatios in T or L at constant R are a signature of the spikes
    # dL, dT, dR = get_diffs(hfile)
    # i = ((np.absolute(dR) <= max_dR) & (np.absolute(dT)+np.absolute(dL)> max_dLT))
    # delta_HR, delta_logR = get_delta_HR_div_delta_logR(hfile)


    # check only late
    # log_center_T = src[:, col.index("log_center_T")]
    # i_hot = (log_center_T >= 8.5) # O ignition based on Sukhbold and Woosley

    # i = np.logical_and(i, i_hot)

    failed_steps = 0 #np.sum(i)
    if do_plot:
        fig = plt.figure()
        gs = gridspec.GridSpec(150, 100)
        ax = fig.add_subplot(gs[:, :])
        # color = np.concatenate(([0],delta_HR/delta_logR))
        # log_center_T = src[:, col.index("log_center_T")]
        # i_hot = (log_center_T >= 8.5) # O ignition based on Sukhbold and Woosley
        # color[i_hot] = 0 # ignore early evol
        # p = ax.scatter(logT, logL, c=color, vmin=-1, vmax=10)
        # plt.colorbar(p)
        ax.plot(logT, logL)
        # ax.scatter(logT[i], logL[i], c='r', marker='x', label=r"excluded "+f"{failed_steps:d}") #, size=200)
        ax.set_title(model.split('/')[-3]+r" "+model.split('/')[-2], fontsize=30)
        annotate_radii_hrd(ax, radii=[0.1, 1, 10])
        ax.invert_xaxis()
        ax.set_xlabel(r"$\log_{10}(T_\mathrm{eff}/[K])$")
        ax.set_ylabel(r"$\log_{10}(L/L_\odot)$")
        plt.savefig(model+"/HRD_check"+
                    f"{src[0, col.index('star_mass')]:.2f}"+
                    r"_rot"+
                    f"{src[100, col.index('surf_avg_omega_div_omega_crit')]:.2f}"+".png")
        plt.close()
    return failed_steps


def list_all_single_models(root):
    """
    finds all the models of given M and initial rotation rate in a
    grid of single stars
    """
    all_single_models = [x for x in glob.glob(root+"/*/*rot*") if "tar" not in x]
    print(all_single_models)
    return all_single_models, len(all_single_models)


def get_ZAMS_omega_div_omega_crit(workdir):
    """ omega_div_omega_crit is not initialized at the beginning of the run, but "near ZAMS" """
    try:
        hfile = workdir+"/LOGS1/history.data"
        src, col = get_src_col(hfile)
    except FileNotFoundError:
        hfile = workdir+"/LOGS/history.data"
        src, col = get_src_col(hfile)
    L = 10.0**src[:, col.index("log_L")] # photospheric L
    L_nuc = 10.**(src[:, col.index("log_Lnuc")]) # nuclear L
    ratio = L_nuc/L
    # ZAMS when ratio ~1
    izams = np.argmin(np.absolute(ratio - 1.0))
    return src[izams, col.index("surf_avg_omega_div_omega_crit")]


def make_success_HRD(root):
    all_single_models, N_models = list_all_single_models(root)
    for workdir in tqdm(all_single_models):
        if (getTerminationCode(workdir) == 'fe_core_infall_limit'):
            try:
                hfile = workdir+"/LOGS1/history.data"
                src, col = get_src_col(hfile)
            except FileNotFoundError:
                hfile = workdir+"/LOGS/history.data"
                src, col = get_src_col(hfile)
            logT = src[:, col.index("log_Teff")]
            logL = src[:, col.index("log_L")]
            fig = plt.figure()
            gs = gridspec.GridSpec(150, 100)
            ax = fig.add_subplot(gs[:, :])
            ax.plot(logT, logL)
            ax.set_title(workdir.split('/')[-3]+r" "+workdir.split('/')[-2], fontsize=30)
            annotate_radii_hrd(ax, radii=[0.1, 1, 10])
            ax.invert_xaxis()
            ax.set_xlabel(r"$\log_{10}(T_\mathrm{eff}/[K])$")
            ax.set_ylabel(r"$\log_{10}(L/L_\odot)$")
            plt.savefig(workdir+"/HRD_check"+
                        f"{src[0, col.index('star_mass')]:.2f}"+
                        r"_rot"+
                        f"{src[100, col.index('surf_avg_omega_div_omega_crit')]:.2f}"+".png")
            plt.close()



def grid_plot(root):
    """ make a plot of the success as a function of Mzams and omega_div_omega_crit """
    fig = plt.figure()
    gs = gridspec.GridSpec(100, 100)
    ax = fig.add_subplot(gs[:, :])
    all_single_models, N_models = list_all_single_models(root)
    for workdir in tqdm(all_single_models):
        try:
            hfile = workdir+"/LOGS1/history.data"
            src, col = get_src_col(hfile)
        except FileNotFoundError:
            hfile = workdir+"/LOGS/history.data"
            src, col = get_src_col(hfile)
        mzams = src[0, col.index('star_mass')]
        omega_div_omega_crit = get_ZAMS_omega_div_omega_crit(workdir)
        print(mzams, omega_div_omega_crit)
        print("check:", hfile)
        success = successful_model(workdir)
        if success:
            ax.scatter(mzams, omega_div_omega_crit, color="g", marker="o", s=100)
        else:
            ax.scatter(mzams, omega_div_omega_crit, color="r", marker="x", s=100)
        print("-----------> m=", mzams, "omega_div_omega_crit", omega_div_omega_crit, "success", success)
    ax.set_xlabel(r"$M_\mathrm{ZAMS} \ [M_\odot]$")
    ax.set_ylabel(r"$\omega_\mathrm{ZAMS}/\omega_\mathrm{crit}$")
    plt.savefig(root+'/overview_grid.png')
    plt.savefig(root+'/overview_grid.pdf')
    print(root+'/overview_grid.png')


def HRD_crossing_out_spikes(model, max_dR = 1e-2, max_dLT = 5e-2, do_plot = True):
    try:
        hfile = model+"/LOGS1/history.data"
        src, col = getSrcCol(hfile)
    except FileNotFoundError:
        hfile = model+"/LOGS/history.data"
        src, col = getSrcCol(hfile)
    logT = src[:, col.index("log_Teff")]
    logL = src[:, col.index("log_L")]

    # large variatios in T or L at constant R are a signature of the spikes
    # dL, dT, dR = get_diffs(hfile)
    # i = ((np.absolute(dR) <= max_dR) & (np.absolute(dT)+np.absolute(dL)> max_dLT))
    # delta_HR, delta_logR = get_delta_HR_div_delta_logR(hfile)


    # check only late
    # log_center_T = src[:, col.index("log_center_T")]
    # i_hot = (log_center_T >= 8.5) # O ignition based on Sukhbold and Woosley

    # i = np.logical_and(i, i_hot)

    failed_steps = 0 #np.sum(i)
    if do_plot:
        fig = plt.figure()
        gs = gridspec.GridSpec(150, 100)
        ax = fig.add_subplot(gs[:, :])
        # color = np.concatenate(([0],delta_HR/delta_logR))
        # log_center_T = src[:, col.index("log_center_T")]
        # i_hot = (log_center_T >= 8.5) # O ignition based on Sukhbold and Woosley
        # color[i_hot] = 0 # ignore early evol
        # p = ax.scatter(logT, logL, c=color, vmin=-1, vmax=10)
        # plt.colorbar(p)
        ax.plot(logT, logL)
        # ax.scatter(logT[i], logL[i], c='r', marker='x', label=r"excluded "+f"{failed_steps:d}") #, size=200)
        ax.set_title(model.split('/')[-3]+r" "+model.split('/')[-2], fontsize=30)
        annotate_radii_hrd(ax, radii=[0.1, 1, 10])
        ax.invert_xaxis()
        ax.set_xlabel(r"$\log_{10}(T_\mathrm{eff}/[K])$")
        ax.set_ylabel(r"$\log_{10}(L/L_\odot)$")
        plt.savefig(model+"/HRD_check"+
                    f"{src[0, col.index('star_mass')]:.2f}"+
                    r"_rot"+
                    f"{src[100, col.index('surf_avg_omega_div_omega_crit')]:.2f}"+".png")
        plt.close()
    return failed_steps


def successful_model(workdir, desired_termcode='fe_core_infall_limit', do_plot=True):
    """
    Given a MESA workdir verifies from output file the desired termination condition
    and the absence of HRD spikes
    """
    if ((getTerminationCode(workdir) == desired_termcode) and
        (HRD_crossing_out_spikes(workdir, do_plot=do_plot) == 0)):
        return True
    return False


def wrapper(workdir, success_cnt = 0, success_list = [], failed_cnt = 0, failed_list = [], N_models = 1):
    termcode = getTerminationCode(workdir)
    if termcode == "no_output":
        N_models -= 1
    else:
        if successful_model(workdir):
            success_cnt +=1
            success_list += [workdir]
        else:
            failed_cnt +=1
            failed_list += [workdir]
    print("done checking ", workdir, termcode)
    return success_cnt, success_list, failed_cnt, failed_list, N_models


def main(root):
    # make_success_HRD(root)
    grid_plot(root)
    success = 0
    all_single_models, N_models = list_all_single_models(root)
    list_success = []
    failed = 0
    list_failed = []
    Parallel(n_jobs=20)(delayed(wrapper)(workdir, success, list_success, failed, list_failed, N_models) for workdir in all_single_models)
    # for workdir in all_single_models:
    #     success, list_success, failed, list_failed, N_models = wrapper(workdir,
    #                                                                    success_cnt = success, success_list = list_success,
    #                                                                    failed_cnt = failed, failed_list = list_failed, N_models = N_models)
    print("")
    print("N_models =", N_models, "success = ", success, "failed = ", failed)
    print("")


if __name__ == "__main__":
    root = "../raw_data/"  # this is the location of the full grid output including failing models
    # main(root)
