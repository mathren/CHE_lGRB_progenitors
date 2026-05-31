#!/usr/local/bin/python
# Authors:
#          Mathieu Renzo <mrenzo@flatironinstitute.org>
#
# Keywords: files

# Copyright (C) 2021 Mathieu Renzo

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

__author__ = ["Mathieu Renzo <mrenzo@arizona.edu>"]

import sys
import os
import glob
import math
import numpy as np
from utilsLib import checkFolder, gitPush
from joblib import Parallel, delayed


def mk_mass_folder(m, WHERE_TO_RUN):
    """ make folder for one mass and various rotation rates"""
    MASS_FOLDER = WHERE_TO_RUN+f"{m:.2f}"+"/"
    os.system("mkdir -p "+MASS_FOLDER)
    for rot in omega_div_omega_crit:
        DESTINATION = MASS_FOLDER+'rot_'+f"{rot:.2f}"+"/"
        os.system("mkdir -p "+DESTINATION)
        os.chdir(DESTINATION)
        # # copy stuff
        copy = "cp -r " + ROOT + TEMPLATE + "/* ./"
        os.system(copy)
        # change mass, rotation, etc...
        with open(DESTINATION+"/inlist1", "r") as I:
            inlist = I.read()
        inlist = inlist.replace("MASS", f"{m:.2f}")
        inlist = inlist.replace("OMEGA_DIV_OMEGA_CRIT", f"{rot:.2f}")
        with open(DESTINATION+"/inlist1", "w") as I:
            I.write(inlist)
        # change rn file for email subject
        with open(DESTINATION+"/rn", "r") as I:
            rn = I.read()
        rn = rn.replace("MASS", f"{m:.2f}")
        rn = rn.replace("OMEGA_DIV_OMEGA_CRIT", f"{rot:.2f}")
        with open(DESTINATION+"/rn", "w") as I:
            I.write(rn)
    print("done mass:", m, "at", MASS_FOLDER)


if __name__ == "__main__":
    # define grid
    mass = np.linspace(30, 100, 71)
    omega_div_omega_crit = [0.0] # np.linspace(0.5, 0.99, 11) #21)
    # adapt to your location
    # folder names need to end with /
    ROOT = "/xdisk/mrenzo/mrenzo/CHE/CHE_jets/"
    TEMPLATE = "single_CHE_template/"
    WHERE_TO_RUN = "/xdisk/mrenzo/mrenzo/CHE/ZAMS_R_non_rot/"
    #
    print(mass)
    print(omega_div_omega_crit)
    print("number of models:", len(mass)*len(omega_div_omega_crit))
    print("template:", ROOT+TEMPLATE)
    print("destination:", WHERE_TO_RUN)
    go_on = input("should we go on? [Y/n]")
    if (go_on == "Y") or (go_on == "y"):
        content = checkFolder(WHERE_TO_RUN)
        if content:  # not empty
            print(str(WHERE_TO_RUN), "is not empty")
            print(content)
            go_on = input("Go on anyways? [Y/y]")
            if go_on != "Y" and go_on != "y":
                sys.exit()
    else:
        sys.exit()
    # push to repo
    gitPush(ROOT, template=TEMPLATE, description=sys.argv[1])
    os.system("mkdir -p "+WHERE_TO_RUN)
    # save template
    os.system(
        "tar -czf template.tar.xz "
        + ROOT + TEMPLATE
        + " && mv template.tar.xz "
        + WHERE_TO_RUN)
    Parallel(n_jobs=10)(delayed(mk_mass_folder)(m, WHERE_TO_RUN) for m in mass)
    # copy local slurm script and edit it
    with open('./run_grid.slurm', 'r') as f:
        runfile = f.read()
    runfile = runfile.replace("GRID_NAME", str(sys.argv[1]).replace(" ", "_"))
    runfile = runfile.replace("N_STARS", str(len(mass)*len(omega_div_omega_crit)))
    runfile = runfile.replace("LIST_MASS", ' '.join(f"{m:.2f}" for m in mass))
    runfile = runfile.replace("LIST_ROT", ' '.join(f"{rot:.2f}" for rot in omega_div_omega_crit))
    runfile = runfile.replace("WHERE_TO_RUN", WHERE_TO_RUN)
    with open(WHERE_TO_RUN+'/run_grid.slurm', 'w') as f:
        f.write(runfile)
    print()
    print("Done setting up a grid of single CHE models at:")
    print(WHERE_TO_RUN)
    print()
