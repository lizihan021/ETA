#!/bin/bash

#SBATCH --job-name=speed20
#SBATCH --partition=fat
#SBATCH --mail-type=end
#SBATCH --mail-user=Steven_Ge@sjtu.edu.cn
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -n 16
#SBATCH --exclusive

ulimit -l unlimited
ulimit -s unlimited

pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db20 -l logfilenew start
python matching_multithread_128.py output_data/20161120/*.gpx
