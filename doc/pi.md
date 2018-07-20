### 1. Install package:

`spack` package manager is installed by Lao Ge. Use `spack install` instead of `sudo apt-get install`. They should have the same results. If the package is not found, you should use `spack create` and `spack edit` and `spack install`. 

**Example**:

```
spack create YOUR_PACKAGE_DOWNLOAD_LINK # github's http link will work
```
Run `spack edit YOUR_PACKAGE_NAME` to add dependencies (Use function `depends_on()`).
Then run `spack install YOUR_PACKAGE_NAME`

Load your package with `module load xxx`. **If you do not load the package, the package appears as if it was not installed.** 

`module list` will show you the currently loaded modules. `module avail` shows the available installed modules.

To list all available packages on `spack`: `spack list` or visit:
https://spack.readthedocs.io/en/latest/package_list.html

### 2. Load modules on start
Edit `.bashrc` in the home directory. Put `module load` at the end.
```
module load postgresql-10.3-gcc-5.4.0-pfaqgqr
```

`postgresql` and `miniconda3` are loaded by default.

### 3. To start psql database

```
pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db -l logfile start     # start psql server 
# -D specifies the database directory
# Notice that one database directory can only run one psql server at one time
psql -h localhost				# connect to psql. run database in commandline
```

### 4. Stop psql database
```
pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db stop
```
Stop the psql server on the database directory if you want to submit a job involving starting a psql server on this database directory on HPC.

### 5.  Use python (if you meet package psycopg2 not found problem, you definitely should do this):
We will use python 2. The default module loaded on HPC is python 3 though.
```
source activate mypython2
```
Package `miniconda3` is required to do this step, and the code to load it has been put in `.bashrc`.

### 6. .slurm script to submit job
To submit a job, do `sbatch edge_speed.slurm`

Here is a sample script to submit a job.
`edge_speed.slurm`

```
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
```

Here, `#SBATCH --partition=fat` specifies the partition to run the job. `cpu`, `cpu128` are also valid partitions.

Before select a partition, you could use command `sinfo` to see which partition has idle nodes.
Run `sacct -a` will show you all the jobs (including others' account) running or pending on HPC.

`#SBATCH -n 16` specifies the number of cpu is required for this job.

Please change the email address, otherwise my mail box will explode.

If your job is queued and you want to log out of SSH before job starts running, you need to add `source activate mypython2` in `.slurm` as well.

### 7. Cancel a job on HPC
Do `scancel YOURJOBID`
Example:
```
scancel 1813612
```

### 8. Track the progress of the jobs
The following command line will show you the status of today's job.
```
sacct --format="JobID, JobName,Partition, AllocCPUS,Elapsed,State"
```

The stdout and stderr of the program will be redirected to YOURJOBID.out and YOURJOBID.err in the directory where you submit your `.slurm` file. `cat YOURJOBID.out` will show the content. `\r` is your friend for print.

### 9. Multi-thread in python
See the main function in `ETA/data-process/edge_speed_multithread.py` for detail.

