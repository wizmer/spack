# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
from spack import *
from contextlib import contextmanager
import shutil
import os
import sys


class NeurodamusModel(Package):
    """An 'abstract' base package for Simulation Models. Therefore no version.
       Eventually in the future Models are independent entities, not tied to neurodamus
    """
    depends_on('neurodamus-core')

    variant('coreneuron',  default=False, description="Enable CoreNEURON Support")
    variant('profile',     default=False, description="Enable profiling using Tau")
    variant('synapsetool', default=True,  description="Enable Synapsetool reader")
    variant('sonata',      default=False, description="Enable Synapsetool with Sonata")
    variant('plasticity',  default=False, description="Use optimized ProbAMPANMDA_EMS and ProbGABAAB_EMS")

    depends_on("mpi")
    depends_on("hdf5+mpi")
    depends_on("neuron+mpi")
    depends_on('reportinglib')
    depends_on('coreneuron', when='+coreneuron')
    depends_on('synapsetool+mpi', when='+synapsetool~sonata')
    depends_on('synapsetool+mpi+sonata', when='+synapsetool+sonata')

    # NOTE: With Spack chain we no longer require support for external libs.
    # However, in some setups (notably tests) some libraries might still be
    # specificed as external and, if static, and we must bring their dependencies.
    depends_on('zlib')  # for hdf5

    depends_on('neuron+profile', when='+profile')
    depends_on('coreneuron+profile', when='+coreneuron+profile')
    depends_on('reportinglib+profile', when='+profile')
    depends_on('tau', when='+profile')

    conflicts('^neuron~python', when='+coreneuron')
    conflicts('+sonata', when='~synapsetool')

    # ---
    phases = ['merge_hoc_mod', 'build', 'install']

    # These vars can be overriden by subclasses to specify additional sources
    # This is required since some models have several sources, e.g.: thalamus
    # By default they use common (which should come from submodule)
    _hoc_srcs = ('common/hoc', 'hoc')
    _mod_srcs = ('common/mod', 'mod')

    # The name of the mechanism, which cen be overriden
    mech_name = ""

    def merge_hoc_mod(self, spec, prefix):
        core_prefix = spec['neurodamus-core'].prefix
        # First Initialize with core hoc / mods
        copy_tree(core_prefix.hoc, '_merged_hoc')
        copy_tree(core_prefix.mod, '_merged_mod')

        # If we shall build mods for coreneuron, only bring from core those specified
        if spec.satisfies("+coreneuron"):
            mkdirp('core_mechs')
            with open(core_prefix.mod.join("coreneuron_modlist.txt")) as core_mods:
                for aux_mod in core_mods:
                    shutil.copy(core_prefix.mod.join(aux_mod.strip()), 'core_mechs')

        if spec.satisfies('+plasticity'):
            copy_all('common/mod/optimized', 'common/mod')

        # Copy from the several sources
        for hoc_src in self._hoc_srcs:
            copy_all(hoc_src, '_merged_hoc')
        for mod_src in self._mod_srcs:
            copy_all(mod_src, '_merged_mod')
            if spec.satisfies("+coreneuron"):
                copy_all(mod_src, 'core_mechs')

    def build(self, spec, prefix):
        """ Build mod files from m dir with nrnivmodl
            To support shared libs, nrnivmodl is also passed RPATH flags.
        """
        force_symlink('_merged_mod', 'm')
        dep_libs = ['reportinglib', 'hdf5',  'zlib']
        profile_flag = '-DENABLE_TAU_PROFILER' if '+profile' in spec else ''

        # Allow deps to not recurs bring their deps
        link_flag = '-Wl,-rpath,' + prefix.lib
        include_flag = ' -I%s -I%s %s' % (spec['reportinglib'].prefix.include,
                                          spec['hdf5'].prefix.include,
                                          profile_flag)
        if '+synapsetool' in spec:
            include_flag += ' -DENABLE_SYNTOOL -I ' + spec['synapsetool'].prefix.include
            dep_libs.append('synapsetool')

        for dep in dep_libs:
            link_flag += ' ' + self._get_lib_flags(spec, dep)

        # If synapsetool is static we have to bring dependencies
        if spec.satisfies('+synapsetool') and spec.satisfies('^synapsetool~shared'):
            link_flag += ' ' + spec['synapsetool'].package.dependency_libs(spec).joined()

        # Create corenrn mods
        if '+coreneuron' in spec:
            include_flag += ' -DENABLE_CORENEURON -I%s' % (spec['coreneuron'].prefix.include)
            corenrnmodl = which('corenrnmodl')
            corenrnmodl('-i', include_flag, '-l', link_flag, '-n', self.mech_name,
                        '-v', str(spec.version), 'core_mechs')
            output_dir = spec.architecture.target + "_core"
            mechlib = find_libraries("libcorenrnmech*", output_dir)
            assert len(mechlib), "Error creating corenrnmech lib"

            #Link neuron special with this mechs lib
            link_flag += ' ' + mechlib.ld_flags + \
                         ' ' + self._get_lib_flags(spec, 'coreneuron')

        nrnivmodl = which('nrnivmodl')
        with profiling_wrapper_on():
            nrnivmodl('-incflags', include_flag, '-loadflags', link_flag, 'm')
        special = os.path.join(os.path.basename(self.neuron_archdir), 'special')
        assert os.path.isfile(special)

    @staticmethod
    def _get_lib_flags(spec, lib_pckg):
        if spec[lib_pckg].satisfies('+shared'):
            # For shared libs we define rpath and ld_flags
            return "%s %s" % (spec[lib_pckg].libs.rpath_flags,
                              spec[lib_pckg].libs.ld_flags)
        else:
            # Otherwise full path is ok. (What about sub-dependencies?)
            return spec[lib_pckg].libs.joined()

    def install(self, spec, prefix):
        """ Move hoc, mod and libnrnmech.so to lib, generated mod.c's into lib/modc.
            Find and move "special" to bin.
            If +coreneuron, install the shared lib to lib/ and corenrn-special to bin.
            If neurodamus-core comes with python, create links under python.
        """
        mkdirp(prefix.bin)
        mkdirp(prefix.lib)
        mkdirp(prefix.share.modc)
        shutil.move('_merged_hoc', prefix.lib.hoc)
        shutil.move('_merged_mod', prefix.lib.mod)

        arch = os.path.basename(self.neuron_archdir)
        shutil.move(join_path(arch, 'special'), prefix.bin)

        # Copy c mods
        for cmod in find(arch, "*.c", recursive=False):
            shutil.move(cmod, prefix.share.modc)

        # Handle non-binary special
        if os.path.exists(arch + "/.libs/libnrnmech.so"):
            shutil.move(arch + "/.libs/libnrnmech.so", prefix.lib)
            sed = which('sed')
            sed('-i', 's#-dll .*#-dll %s#' % prefix.lib.join('libnrnmech.so'),
                prefix.bin.special)

        # TODO: Corenrn
        if spec.satisfies('+coreneuron'):
            shutil.move("modc_core", prefix.share)
            outdir = spec.architecture.target + '_core'
            shutil.move(join_path(outdir, 'corenrn-special'), prefix.bin)
            for libname in find_libraries("libcorenrnmech*", outdir):
                shutil.move(libname, prefix.lib)

        # PY: Link only important stuff, and create a new lib link (to our lib)
        py_src = spec['neurodamus-core'].prefix.python
        if os.path.isdir(py_src):
            pydir = prefix.lib.python
            mkdirp(py_dst)
            force_symlink('../lib', py_dst.lib)
            for name in ('neurodamus', 'init.py', '_debug.py'):
                os.symlink(py_src.join(name), py_dst.join(name))

    def setup_environment(self, spack_env, run_env):
        run_env.prepend_path('PATH', self.prefix.bin)
        run_env.set('HOC_LIBRARY_PATH', self.prefix.lib.hoc)

        if os.path.isdir(self.prefix.python):
            for m in spack_env.env_modifications:
                if m.name == 'PYTHONPATH':
                    run_env.prepend_path('PYTHONPATH', m.value)
            run_env.prepend_path('PYTHONPATH', self.prefix.python)
            run_env.set('NEURODAMUS_PYTHON', self.prefix.python)

@contextmanager
def profiling_wrapper_on():
    os.environ["USE_PROFILER_WRAPPER"] = "1"
    yield
    del os.environ["USE_PROFILER_WRAPPER"]


# Aux funcs
# ---------
def copy_all(src, dst, copyfunc=shutil.copy):
    """Copies/processes all files in a src dir against a destination dir"""
    print("Copying " + src + " to " + dst)
    isdir = os.path.isdir
    for name in os.listdir(src):
        print(" > file " + name)
        pth = join_path(src, name)
        isdir(pth) or copyfunc(pth, dst)


def symlink2(src, dst):
    """Simple alternative to symlink, copy compat"""
    if os.path.isdir(dst):
        dst_dir = dst
        dst = join_path(dst, os.path.basename(src))
    else:
        dst_dir = os.path.dirname(dst)
    src = os.path.relpath(src, dst_dir) # update path relation
    os.symlink(src, dst)


def filter_out(src, dst):
    """Remove src from dst, copy compat"""
    try:
        os.remove(join_path(dst, os.path.basename(src)))
    except: pass

# Shortcut to extra operators
copy_all.symlink2 = symlink2
copy_all.filter_out = filter_out
