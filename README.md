# THIS REPO IS NO LONGER BEING UPDATED!!

An updated version is being maintained by [The ARC Centre of Excellence for the Weather of the 21st Century](https://www.21centuryweather.org.au):

https://github.com/21centuryweather/nci_scripts




Helpful scripts for working at NCI
==================================

To use these scripts on NCI infrastructure do the following:

```
module use /g/data/hh5/public/modules
module load nci-scripts
```

uqstat
------

Show extended information for jobs in the queue

```
$ uqstat
                Job_Name       queue state  ncpus walltime   su     mem_pct    cpu_pct    qtime
961571.gadi-pbs    STDIN  copyq-exec     R      1 01:26:18  3.0  100.000191  85.940518 00:10:00
```

qcost
------

Calculates what it would cost, in SU, for a job submitted to the PBS system with the same configuration. 
The information is all contained in the [PBS queue information is provided by NCI](https://opus.nci.org.au/display/Help/Queue+Limits)
but it can be tedious to determine which configuration of queue and memory request should be used
to minimise job cost. `qcost` was created to make this process easier.

Usage:
```
./qcost -h
usage: qcost [-h] -q QUEUE -n NCPUS -m MEM [-t TIME]

Return what it would cost (in SUs) for a PBS job submitted on gadi with the same               
configuration. No checking is done to ensure requests are within queue limits.                 


optional arguments:
  -h, --help            show this help message and exit
  -q QUEUE, --queue QUEUE
                        PBS queue
  -n NCPUS, --ncpus NCPUS
                        Number of cpus
  -m MEM, --mem MEM     Requested memory
  -t TIME, --time TIME  Job walltime (hours)

e.g. qcost -q normal -n 4 -m 60GB -t 3:00:00
```

Note that if no time is specified it defaults to 1 hour (`1:00:00`). Walltime can be specified as `H:M` or `H:M:S`. Memory must be specified in units of bytes (`B`), e.g. `160GB`, `2000MB`

Example and output:
```
$ qcost -q normal -n 4 -m 60GB -t 3:00:00
90 SU
```

gadi_jupyter
------------

Run a Jupyter notebook on Gadi, displaying it in a local web browser. 

**THIS MUST BE RUN FROM YOUR OWN COMPUTER**

So the first step is to clone this repository to your local workstation. It
works on mac/linux/windows (for windows using e.g. [git bash](https://gitforwindows.org/)
or [Windows Ssubsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install)).

By default the script will spawn a job with a single CPU, 4GB of memory 
and a walltime of 1 hour.

Command line options can be used to alter the resources requested, the
conda environment used to spawn the job and NCI username

Usage:
```
gadi_jupyter -h

Run a Jupyter notebook on Gadi's compute nodes, presenting the interface in a
browser on the local machine

You can set a default username in your local ~/.ssh/config, e.g.

    Host gadi.nci.org.au
    User abc123

Your default project is set in the file on Gadi ~/.config/gadi-login.conf

General Options:
    -h:         Print help
    -l USER:    NCI username
    -L HOST:    NCI login node (default 'gadi.nci.org.au')
    -e ENVIRON: Conda environment
    -d:         Debug mode

Queue Options:
    -q QUEUE:   Queue name
    -n NCPU:    Use NCPU cpus
    -m MEM:     Memory allocation (default 4*NCPU GB)
    -t TIME:    Walltime limit (default 1 hour)
    -J JOBFS:   Jobfs allocation (default 100 GB)
    -P PROJ:    Submit job under project PROJ
    -s STORAGE: PBS Storage flags (e.g. 'scratch/w35+gdata/v45')
                If not specified, all available storage is requested

```

You will need to have ssh keys setup for logging into gadi. There is a 
[guide on how to do this on the CMS Wiki](http://climate-cms.wikis.unsw.edu.au/CLEx_induction#Step_2:_Set_up_your_Connection).

vdi_jupyter.py
--------------

Run a Jupyter notebook on 
[NCI Virtual Desktop Infrastructure (VDI)](https://opus.nci.org.au/display/Help/VDI+User+Guide), displaying it in a local web browser (run from your own computer).

To run:
```
python nci_scripts/vdi_jupyter.py
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


**Note for Windows Users:**
The `pexpect` package for Windows doesn't have the required functionality for running this script, so running the script will return an error. If you have Windows 10, you can [install the Windows Subsystem for Linux (WSL or WSL 2)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) allowing you to set up a Linux environment on your Windows machine in which it will run.


qsubs
-----

`qsub` but it requests all of the `-l storage=` options for projects you're a member of


cloudstor
---------

Upload data to https://cloudstor.aarnet.edu.au

gdata-info
----------

Information about what projects are on which NCI Gdata mount

Available projects on gdata1a:
```
$ gdata-info -m gdata1a
e14
ks32
p66
p73
rr3
```

The gdata system for project e14:
```
$ gdata-info -P e14
gdata1a
```
