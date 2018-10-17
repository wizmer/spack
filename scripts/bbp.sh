#!/bin/bash
set -e

BASE_RESULT_DIR="`pwd`/RESULTS/bbp/`date +"%a-%d-%m-%Y-%H-%M"`"
mkdir -p $BASE_RESULT_DIR

# Redirect stdout ( > ) into a named pipe ( >() ) running "tee"
exec > >(tee $BASE_RESULT_DIR/run.log)
exec 2>&1

# load profile or non-profiled versions
module purge all
module load neuron neuronmodels/bbp$1

mpilauncher="srun"
sim_time=5
# profile format
export TAU_PROFILE_FORMAT=merged
export OMP_NUM_THREADS=1
export MV2_CPU_BINDING_POLICY=bunch
export I_MPI_PIN_DOMAIN=core
export I_MPI_PIN_ORDER=compact
export MPI_PIN_PROCESSOR_LIST=all:map=bunch
export HDF5_DISABLE_VERSION_CHECK=1

cd $BASE_RESULT_DIR
cp $MODEL_DIR/circuit/build/circuitBuilding_1000neurons/BlueConfig .

# Running with NEURON
for nproc in 36 18 9; do
    set -x
    sed -i "s/Simulator.*/Simulator NEURON/g" BlueConfig
    $mpilauncher -n $nproc special -mpi $MODEL_DIR/hoc/init.hoc &> nrn.$nproc.log
    set +x
    sortspike out.dat out.dat.nrn.$nproc
    [[ -f $tau_file ]] && mv $tau_file tau.nrn.$nproc.xml
    sol_time=$(grep psolve nrn.$nproc.log | grep -Eo '[0-9]+.[0-9]+$')
    echo "[NEURON] Running with $nproc rank took : $sol_time seconds"
done

# Running with CoreNEURON
for nproc in 36 18 9; do
    set -x
    sed -i "s/Simulator.*/Simulator CORENEURON/g" BlueConfig
    $mpilauncher -n $nproc special -mpi $MODEL_DIR/hoc/init.hoc &> cnrn.$nproc.log
    set +x
    sortspike out.dat out.dat.cnrn.$nproc
    [[ -f $tau_file ]] && mv $tau_file tau.cnrn.$nproc.xml
    sol_time=$(grep Solver cnrn.$nproc.log | sed 's/Solver Time ://')
    echo "[CoreNEURON] Running with $nproc rank took : $sol_time seconds"
done
