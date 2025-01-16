#!/bin/bash
#SBATCH -J CeO2-100-CeO4-H2ads2-new-CONTCAR
#SBATCH -p cnCPU      ### QUEUE
#SBATCH -N 1             ### NUM.of.NODES
#SBATCH -c 36           ### NUM.of.CORES

# executable file
EXEC=/home/ecust_gongxq/ddn/apps/vasp.5.4.4-TS/vasp_std

ulimit -s unlimited
ulimit -l unlimited

. /etc/bashrc
. /apps/modules/latest/init/profile.sh
module load compilers/intel/psxe_2020_u4.mpi 
module load compilers/intel/psxe_2020_u4.ifort

mpirun -np 36 $EXEC > print_out 2>&1 

echo `date` >> ~/ddn/finish
echo `pwd` >> ~/ddn/finish

