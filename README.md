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

Run a Jupyter notebook on Gadi, displaying it in a local web browser 
(run from your own computer)i.

By default the script will spawn a job with a single CPU, 4GB of memory 
and a walltime of 1 hour.

Command line options can be used to alter the resources requested, the
conda environment used to spawn the job and NCI username

Usage:
```
gadi_jupyter -h
Run a Jupyter notebook on Gadi's compute nodes, presenting the 
interface in a browser on the local machine

General Options:
    -h:         Print help
    -l:         NCI username
    -L:         NCI login node (default 'gadi.nci.org.au')
    -e:         Conda environment

Queue Options:
    -q QUEUE:   Queue name
    -n NCPU:    Use NCPU cpus
    -m MEM:     Memory allocation (default 4*NCPU GB)
    -t TIME:    Walltime limit (default 1 hour)
    -J JOBFS:   Jobfs allocation (default 100 GB)
    -P PROJ:    Submit job under project PROJ
```

You will need to have ssh keys setup for logging into gadi. There is a 
[guide on how to do this on the CMS Wiki](http://climate-cms.wikis.unsw.edu.au/CLEx_induction#Step_2:_Set_up_your_Connection).

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
