##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
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
import sys
from contextlib import contextmanager


class ChannelBenchmark(Package):
    """Package used for building special from NeurodamusBase package
    """

    homepage = "ssh://bbpcode.epfl.ch/user/kumbhar/channel-benchmark"
    url = "ssh://bbpcode.epfl.ch/user/kumbhar/channel-benchmark"
    #url = "file:///Users/kumbhar/workarena/repos/bbp/channel_benchmark"

    version('develop', git=url)

    depends_on("neuron+mpi")
    depends_on('coreneuron@channel-benchmark')

    def install(self, spec, prefix):
        shutil.copytree('lib', '%s/lib' % (prefix), symlinks=False)

        with working_dir(prefix):
            env['MAKEFLAGS'] = '-j{0}'.format(make_jobs)
            include_flag = ' -DENABLE_CORENEURON -I%s' % (spec['coreneuron'].prefix.include)

            if spec['coreneuron'].satisfies('+shared'):
                link_flag = " %s %s" % (spec['coreneuron'].libs.rpath_flags, spec['coreneuron'].libs.ld_flags)
            else:
                link_flag = " " + spec['coreneuron'].libs.joined()

            nrnivmodl = which('nrnivmodl')
            nrnivmodl('-incflags', include_flag, '-loadflags', link_flag, 'lib/modlib')
            arch = os.path.basename(self.neuron_archdir)
            special = os.path.join(arch, 'special')
            assert os.path.isfile(special)
            shutil.move(os.path.join(arch, 'special'), prefix.bin)

    def setup_environment(self, spack_env, run_env):
        run_env.prepend_path('PATH', self.prefix.bin)
        run_env.set('HOC_LIBRARY_PATH', self.prefix.lib.hoclib)
