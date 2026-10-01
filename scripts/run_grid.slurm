#!/bin/bash

#SBATCH --job-name=GRID_NAME
#SBATCH --account=binboom
#SBATCH --partition=standard
#SBATCH --error=error_%A_%a.err
#SBATCH --array=1-N_STARS
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mail-type=END
#SBATCH --mail-user=mrenzo@arizona.edu
#SBACTH --time=48:00:00


#define parameters
period_pars=(LIST_PERIODS)

#find number of elements and check array indexing
periods_mass=${#period_pars[@]}
echo "total runs" $num_periods

#print current combination of parameters
task_id=$((SLURM_ARRAY_TASK_ID - 1)) #0 versus 1 based indexing
PERIOD_VALUE=${period_pars[$task_id]}

echo "SLURM_JOB_ID=$SLURM_JOB_ID - $SLURM_ARRAY_TASK_ID"
echo "Starting job: P = $PERIOD_VALUE"

#single
FOLDER_NAME=$PERIOD_VALUE


cd WHERE_TO_RUN$FOLDER_NAME
export OMP_NUM_THREADS=8
export MESASDK_ROOT=/home/u20/mrenzo/codes/mesa/mesasdk
source $MESASDK_ROOT/bin/mesasdk_init.sh
export MESA_DIR=/home/u20/mrenzo/codes/mesa/mesa-24.08.1/

echo "-------------"
hostname
echo "Run is in " WHERE_TO_RUN$FOLDER_NAME
echo "MESA_DIR=" $MESA_DIR
echo "SDK ROOT=" $MESASDK_ROOT
gfortran --version
pwd
echo "-------------"

./clean
./mk
./rn
./clean # remove executables after run
