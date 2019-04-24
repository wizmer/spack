# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
from contextlib import contextmanager
import os, shutil


class SimModel(Package):
    """The abstract base package for simulation models.

    Simulation models are groups of nmodl mechanisms. These packages are
    deployed as neuron/coreneuron modules (dynamic loadable libraries)
    which are loadable using load_dll() or linked into a "special"

    """
    variant('coreneuron',  default=False, description="Enable CoreNEURON Support")

    depends_on('neuron~binary+mpi')
    depends_on('coreneuron', when='+coreneuron')

    phases=('build', 'install')


    def build(self, spec, prefix):
        profile_flag = '-DENABLE_TAU_PROFILER' if '+profile' in spec else ''
        link_flag = '-Wl,-rpath,' + prefix.lib
        include_flag = ''

        if '+coreneuron' in spec:
            raise NotImplementedError("Coreneuron support not implemented yet")

        with profiling_wrapper_on():
            which('nrnivmodl')('-incflags', include_flag, '-loadflags', link_flag, 'mod')
        special = os.path.join(os.path.basename(self.neuron_archdir), 'special')
        assert os.path.isfile(special)

    def install(self, spec, prefix):
        """ Install:
              bin/ <- special and special-core
              lib/ <- hoc, mod and lib*mech*.so
              share/ <- neuron & coreneuron mod.c's (modc and modc_core)
        """
        mkdirp(prefix.bin)
        mkdirp(prefix.lib)
        mkdirp(prefix.share.modc)

        arch = os.path.basename(self.neuron_archdir)
        shutil.move(join_path(arch, 'special'), prefix.bin)
        shutil.move(arch + "/.libs/libnrnmech.so", prefix.lib)
        which('sed')('-i',
                     's#-dll .*#-dll %s#' % prefix.lib.join('libnrnmech.so'),
                     prefix.bin.special)

        # Copy original and translated c mods (for neuron)
        shutil.move('mod', prefix.lib.mod)
        for cmod in find(arch, "*.c", recursive=False):
            shutil.move(cmod, prefix.share.modc)

    def setup_environment(self, spack_env, run_env):
        run_env.set('BGLIBPY_MOD_LIBRARY_PATH',
                    self.spec.prefix.lib.join('libnrnmech.so'))


@contextmanager
def profiling_wrapper_on():
    os.environ["USE_PROFILER_WRAPPER"] = "1"
    yield
    del os.environ["USE_PROFILER_WRAPPER"]



