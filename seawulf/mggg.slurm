#!/usr/bin/env bash

#SBATCH --nodes=1
#SBATCH --time=05:00
#SBATCH --partition=short-40core
#SBATCH --job-name=mggg
#SBATCH --output=output.txt

#load required modules

module load 