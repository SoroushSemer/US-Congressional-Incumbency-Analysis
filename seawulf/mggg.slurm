#!/usr/bin/env bash

#SBATCH --nodes=1
#SBATCH --time=3-12:30:00
#SBATCH --partition=extended-96core
#SBATCH --job-name=pirates_mggg_job

# Check https://it.stonybrook.edu/help/kb/seawulf-queues for other queues.

#load required modules

module load gerrychain/0.2.17

# Run python script
python seawulf_code.py