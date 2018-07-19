#!/bin/bash

#SBATCH --job-name=speed30
#SBATCH --partition=cpu
#SBATCH --mail-type=end
#SBATCH --mail-user=Steven_Ge@sjtu.edu.cn
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -n 16
#SBATCH --exclusive

ulimit -l unlimited
ulimit -s unlimited

pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db -l logfilenew start
python matching.py output_data/20161130/*.gpx
