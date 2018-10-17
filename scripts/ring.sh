#!/bin/bash
set -e

BASE_RESULT_DIR="`pwd`/RESULTS/ring/`date +"%a-%d-%m-%Y-%H-%M"`"
mkdir -p $BASE_RESULT_DIR

# Redirect stdout ( > ) into a named pipe ( >() ) running "tee"
exec > >(tee $BASE_RESULT_DIR/run.log)
exec 2>&1

# load profile or non-profiled versions
module purge all
module load neuron neuronmodels/ring$1

# profile format
export TAU_PROFILE_FORMAT=merged
export OMP_NUM_THREADS=1

cd $BASE_RESULT_DIR

sim_time=10
network_params="-nring 16 -ncell 256 -branch 32 64 -compart 16 16"
network_params="-nring 2 -ncell 256 -branch 32 64 -compart 16 16"
tau_file=tauprofile.xml

if [[ ! -f $MODEL_DIR/ringtest.py ]];
then
    echo "Can't find special or $MODEL_DIR"
    exit 1
fi

# Running with NEURON
for nproc in 32 16 8 4 2; do
    set -x
    srun -n $nproc special -python -mpi $MODEL_DIR/ringtest.py $network_params -tstop $sim_time -coredat coredat &> nrn.$nproc.log
    set +x
    sortspike coredat/spk$nproc.std out.dat.nrn.$nproc
    [[ -f $tau_file ]] && mv $tau_file tau.nrn.ring.$nproc.xml
    sol_time=$(grep Solver nrn.$nproc.log | sed 's/Solver Time ://')
    echo "[NEURON] Running with $nproc rank took : $sol_time seconds"
done

# Running with CoreNEURON
for nproc in 32 16 8 4 2; do
    #export PROFILEDIR=cneuron.$nproc.tau
    set -x
    srun -n $nproc special -python -mpi $MODEL_DIR/ringtest.py $network_params -tstop $sim_time -coredat coredat -runcn &> cnrn.$nproc.log
    set +x
    sortspike out.dat out.dat.cnrn.$nproc
    [[ -f $tau_file ]] && mv $tau_file tau.cnrn.ring.$nproc.xml
    sol_time=$(grep Solver cnrn.$nproc.log | sed 's/Solver Time ://')
    echo "[CoreNEURON] Running with $nproc rank took : $sol_time seconds"
done
