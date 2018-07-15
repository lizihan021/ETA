#!/bin/bash

#SBATCH --job-name=06-10
#SBATCH --partition=cpu
#SBATCH --mail-type=end
#SBATCH --mail-user=Steven_Ge@sjtu.edu.cn
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -n 1
#SBATCH --exclusive

ulimit -l unlimited
ulimit -s unlimited

python gps2gpx_mulithread.py
