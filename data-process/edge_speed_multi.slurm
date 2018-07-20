#!/bin/bash

#SBATCH --job-name=speed28
#SBATCH --partition=cpu128
#SBATCH --mail-type=end
#SBATCH --mail-user=Steven_Ge@sjtu.edu.cn
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -n 1
#SBATCH --exclusive

ulimit -l unlimited
ulimit -s unlimited

pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db -l logfilenew start
python matching_multithread.py output_data/20161128/*.gpx
