### 1.install package:

`spack` package manager is installed by Lao Ge. Use `spack install` instead of `sudo apt-get install`. They should have the same results.

Check your installed package with `module avail`.

Load your package with `module load xxx`.

##### Example:

(I have installed psql). To start psql database:

```
module load postgresql-10.3-gcc-5.4.0-pfaqgqr   # load package
pg_ctl -D /lustre/home/acct-umjmcb/umjmcb/db -l logfile start     # start psql server
psql -h localhost				# connect to psql.
```

Handily available packages on spack
https://spack.readthedocs.io/en/latest/package_list.html