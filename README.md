Helpful scripts for working at NCI
==================================

uqstat
------

Show extended information for jobs in the queue

```
$ uqstat
                Job_Name       queue state  ncpus walltime   su     mem_pct    cpu_pct    qtime
961571.gadi-pbs    STDIN  copyq-exec     R      1 01:26:18  3.0  100.000191  85.940518 00:10:00
```

gadi_jupyter
------------

Run a Jupyter notebook on Gadi, displaying it in a local web browser (run from your own computer)

jupyter_vdi.py
--------------

Run a Jupyter notebook on 
[NCI Virtual Desktop Infrastructure (VDI)](https://opus.nci.org.au/display/Help/VDI+User+Guide), displaying it in a local web browser (run from your own computer).

To run:
```
python nci_scripts/jupyter_vdi.py
```

This script requires the `pexpect` package. To make a `conda` environment with the required 
packages:
```
conda env create -f nci_scripts/vdi_environment.yml
``` 
then activate the environment:
```
conda activate jupyter_vdi
```
and run the script as above.

qsubs
-----

`qsub` but it requests all of the `-l storage=` options for projects you're a member of
