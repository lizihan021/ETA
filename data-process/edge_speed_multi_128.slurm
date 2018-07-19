#!/bin/bash

#SBATCH --job-name=speed2627
#SBATCH --partition=cpu128
#SBATCH --mail-type=end
#SBATCH --mail-user=Steven_Ge@sjtu.edu.cn
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -n 64
#SBATCH --exclusive

ulimit -l unlimited
ulimit -s unlimited

pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db -l logfilenew start
python matching_multithread_128.py output_data/20161126/*.gpx &
python matching_multithread_128.py output_data/20161127/*.gpx &
