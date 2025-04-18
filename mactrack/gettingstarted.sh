#!/bin/bash
#SBATCH -n 1
#SBATCH -c 16
#SBATCH -t 30
#SBATCH --job-name=gettingstarted
#SBATCH -o gs.txt
#SBATCH --error=gettingstarted.txt

srun python /home/gbouland/Stage-LPHI-2024/mactrack/gettingstarted_norma.py
