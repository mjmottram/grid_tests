#!/bin/bash

echo "RUNNING AT $1"
uname -a
rpm -q -a | grep cvmfs
ls /cvmfs/snoplus.gridpp.ac.uk
source /cvmfs/snoplus.gridpp.ac.uk/sl6/sw/4.5.0/env_rat-4.5.0.sh
rat -N 5 -o ratoutput -l rat.log ${RATROOT}/mac/production/water/Signal_618.mac
ls
echo "EXITING AT $1"
