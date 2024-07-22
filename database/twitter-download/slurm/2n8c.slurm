#!/bin/bash
#SBATCH --job-name="2n8c"
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --time=00:05:00

module load mpi4py/3.1.4
cd /home/zep/assignment1_2024/code
time srun -n 8 python3 main.py twitter-50mb

##DO NOT ADD/EDIT BEYONG THIS LINE##
##Job monitor command to list the resource usage
my-job-stats -a -n -s

