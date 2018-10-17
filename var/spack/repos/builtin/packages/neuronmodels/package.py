#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
import os
import shutil

class Neuronmodels(Package):
    """NEURON/CoreNEURON models for testing and benchmarking"""

    homepage = "https://github.com/pramodk/neuronmodels"
    url      = "https://github.com/pramodk/neuronmodels.git"

    version('coretest', git=url, submodules=True)
    version('ring', git=url, submodules=True, preferred=True)
    version('traub', git=url, submodules=True)
    version('bbp', git=url, submodules=True)

    variant('gpu', default=False, description="Enable GPU build")
    variant('knl', default=False, description="Enable KNL specific flags")
    variant('mpi', default=True, description="Enable MPI support")
    variant('openmp', default=True, description="Enable OpenMP support")
    variant('profile', default=False, description="Enable profiling using Tau")
    variant('report', default=True, description="Enable reports using ReportingLib")

    for version in ['coretest', 'ring', 'traub', 'bbp']:
        if version == 'bbp':
            depends_on('coreneuron@%s +report+shared' % version, when='@%s' % version)
            depends_on('hdf5')
            depends_on('reportinglib')
            depends_on('zlib')
        else:
            depends_on('coreneuron@%s ~report+shared' % version, when='@%s' % version)

    depends_on('mpi', when='+mpi')
    depends_on('neuron+profile', when='+profile')
    depends_on('neuron~profile', when='~profile')
    depends_on('coreneuron+profile', when='+profile')
    depends_on('coreneuron~profile', when='~profile')
    depends_on('tau~openmp', when='+profile')
    depends_on('neuronmodelresource', when='@coretest @ring @traub @bbp')

    @run_before('install')
    def profiling_wrapper_on(self):
        if self.spec.satisfies('+profile'):
            os.environ["USE_PROFILER_WRAPPER"] = "1"

    @run_after('install')
    def profiling_wrapper_off(self):
        if self.spec.satisfies('+profile'):
            del os.environ["USE_PROFILER_WRAPPER"]

    def check_install(self):
        special = '%s/special' % os.path.basename(self.neuron_archdir)
        if not os.path.isfile(special):
            raise RuntimeError("Installation check failed (%s)!" % special)

    def create_special(self, incflags, ldflags, modir):
        nrnivmodl = which('nrnivmodl')
        nrnivmodl('-incflags', incflags, '-loadflags', ldflags, modir)
        self.check_install()

    def get_model_dir(self):
        spec = self.spec
        models = self.spec['neuronmodelresource'].prefix.models
        model_dir = '%s/%s' % (models, spec.version)
        return model_dir

    def setup_tau_environment(self):
        spec = self.spec
        if (spec.satisfies('+profile')):
	    tau_file = self.stage.source_path + "/tau/instrumentation.tau"
            tau_opts = "-optPDTInst -optNoCompInst -optRevert -optVerbose"
            tau_opts += " -optTauSelectFile=%s" % tau_file
            if (spec.satisfies('+mpi')):
                tau_opts += " -optAppCC=%s" % spec['mpi'].mpicc
                tau_opts += " -optAppCXX=%s" % spec['mpi'].mpicxx
            os.environ["TAU_OPTIONS"] = tau_opts

    def get_inc_flags(self):
        spec = self.spec
        inc_flag  = '-DENABLE_TAU_PROFILER' if '+profile' in spec else ''
        inc_flag += ' -DENABLE_CORENEURON -I%s' % spec['coreneuron'].prefix.include
        if spec.satisfies('@bbp'):
            inc_flag += ' -I%s' %  spec['reportinglib'].prefix.include
        return inc_flag

    def get_link_flags(self):
        spec = self.spec
        link_flag = ' %s' % (spec['coreneuron'].libs.ld_flags)
        if spec.satisfies('@bbp'):
            link_flag += ' %s -L%s -lhdf5 -L%s -lz' % (
                            spec['reportinglib'].libs.ld_flags,
                            spec['hdf5'].prefix.lib,
                            spec['zlib'].prefix.lib)
        return link_flag

    def install(self, spec, prefix):
        model_dir = self.get_model_dir()
        link_flag = ' %s' % spec['coreneuron'].libs.ld_flags

        with working_dir(prefix):
            shutil.copytree(model_dir, str(spec.version), symlinks=False)
            mod_dir = '%s/mod' % spec.version
            self.setup_tau_environment()
            self.create_special(self.get_inc_flags(), self.get_link_flags(), mod_dir)

    def setup_environment(self, spack_env, run_env):
        prefix = self.prefix
        arch_dir = os.path.basename(self.neuron_archdir)
        exe_path = '%s/%s' % (prefix, arch_dir)
        cnrn_lib = self.spec['coreneuron'].libs[0]
        run_env.prepend_path('PATH', exe_path)
        run_env.prepend_path('HOC_LIBRARY_PATH', self.hoc_path)
        run_env.prepend_path('PYTHONPATH', self.python_path)
        run_env.set('MODEL_DIR', self.get_model_dir())
        run_env.set('CORENEURONLIB', cnrn_lib)
