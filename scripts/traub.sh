#!/bin/bash
set -e

BASE_RESULT_DIR="`pwd`/RESULTS/traub/`date +"%a-%d-%m-%Y-%H-%M"`"
mkdir -p $BASE_RESULT_DIR

# Redirect stdout ( > ) into a named pipe ( >() ) running "tee"
exec > >(tee $BASE_RESULT_DIR/run.log)
exec 2>&1

# load profile or non-profiled versions
module purge all
module load neuron neuronmodels/traub$1

mpilauncher="srun"
sim_time=5
network_params="-c one_tenth_ncell=0 -c mytstop=$sim_time"
# profile format
export TAU_PROFILE_FORMAT=merged
export OMP_NUM_THREADS=1

cd $BASE_RESULT_DIR

# Running with NEURON
for nproc in 32 16 8 4; do
    set -x
    $mpilauncher -n $nproc special -mpi $network_params -c coreneuron=0 $MODEL_DIR/run.hoc &> nrn.$nproc.log
    set +x
    sortspike out$nproc.dat out.dat.nrn.$nproc
    [[ -f $tau_file ]] && mv $tau_file tau.nrn.$nproc.xml
    sol_time=$(grep Solver nrn.$nproc.log | sed 's/Solver Time ://')
    echo "[NEURON] Running with $nproc rank took : $sol_time seconds"
done

# Running with CoreNEURON
for nproc in 32 16 8 4; do
    set -x
    $mpilauncher -n $nproc special -mpi $network_params -c coreneuron=1 $MODEL_DIR/run.hoc &> cnrn.$nproc.log
    set +x
    sortspike out.dat out.dat.cnrn.$nproc
    [[ -f $tau_file ]] && mv $tau_file tau.cnrn.$nproc.xml
    sol_time=$(grep Solver cnrn.$nproc.log | sed 's/Solver Time ://')
    echo "[CoreNEURON] Running with $nproc rank took : $sol_time seconds"
done
