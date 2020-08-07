# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyBglibpy(PythonPackage):
    """Pythonic Blue Brain simulator access"""
    homepage = "https://bbpcode.epfl.ch/code/#/admin/projects/sim/BGLibPy"
    url = "ssh://bbpcode.epfl.ch/sim/BGLibPy"
    git = "ssh://bbpcode.epfl.ch/sim/BGLibPy"

    version('develop', branch='master')

    version('4.3', commit='61293ef3f64a18e7a336d7a5a959020c8237b207')
    version('4.2.23', commit='4f88c9df716ca1c7b1c779ee934b28aa991a366b')
    version('4.1.4', commit='e54d294460e5bdf6b9990bc10a4606b412b76d90')

    depends_on('py-setuptools', type=('build', 'run'))

    depends_on('neuron+python', type='run')
    depends_on('py-h5py~mpi@2.3:', type='run')
    depends_on('py-bluepy', type='run')
    depends_on('py-libsonata', type='run')

    def setup_run_environment(self, env):
        env.set('NEURON_INIT_MPI', "0")
        env.unset('PMI_RANK')
