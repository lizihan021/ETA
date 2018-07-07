### 1. Install package:

`spack` package manager is installed by Lao Ge. Use `spack install` instead of `sudo apt-get install`. They should have the same results. If the package is not found, you should use `spack create` and `spack edit` and `spack install`. 

**Example**:

(老葛来写个 example 吧。)

Check your installed package with `module avail`.

Load your package with `module load xxx`. **If you do not load the package, the package appears as if it was not installed.** 

To list all available packages on `spack`: `spack list` or visit:
https://spack.readthedocs.io/en/latest/package_list.html

### 2. To start psql database

```
module load postgresql-10.3-gcc-5.4.0-pfaqgqr   # load package
pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db -l logfile start     # start psql server
psql -h localhost				# connect to psql.
```

### 3.  Use python:

```
source activate mypython2
```