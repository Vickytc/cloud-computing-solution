#!/bin/bash
#SBATCH --job-name="1n1c"
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:10:00

module load mpi4py/3.1.4
cd /home/zep/assignment1_2024/code
time srun -n 1 python3 main.py twitter-100gb

##DO NOT ADD/EDIT BEYONG THIS LINE##
##Job monitor command to list the resource usage
my-job-stats -a -n -s
