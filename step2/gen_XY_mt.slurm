#!/bin/bash

#SBATCH --job-name=gen_XY_mt
#SBATCH --partition=fat
#SBATCH --mail-type=all
#SBATCH --mail-user=wangzizhao@sjtu.edu.cn
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH -n 16
#SBATCH --exclusive

ulimit -l unlimited
ulimit -s unlimited

pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db -l logfilenew start
source activate mypython2
python gen_XY_mt.py
