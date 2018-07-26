##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
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
import os.path as osp
from spack import *


class Nix(AutotoolsPackage):
    """Nix, the purely functional package manager"""

    homepage = "http://nixos.org/nix"
    url      = "https://github.com/NixOS/nix/archive/2.0.4.zip"

    version('2.0.4', '045adeb4714f559386e391cc3c411710')

    patch('fix-doc-build.patch')

    variant('storedir', values=str, default=None,
            description='path of the Nix store (defaults to /nix)')
    variant('statedir', values=str, default=None,
            description='path to the locale state (defaults to /nix/var)')
    variant('doc', values=bool, default=True,
            description="Build and install documentation")
    variant('sandboxing', values=bool, default=True,
            description='Enable build isolation')
    variant('stdlibrpath', values=bool, default=True,
            description='Add compiler library dir to Nix executables rpath')

    depends_on('autoconf', type='build')
    depends_on('automake', type='build')
    depends_on('bison', type='build')
    depends_on('flex', type='build')
    depends_on('libtool', type='build')
    depends_on('libxslt', when="+doc", type='build')
    depends_on('m4', type='build')

    depends_on('curl')
    depends_on('libseccomp', when="+sandboxing")
    depends_on('sqlite')
    depends_on('xz')

    # gcc 4.9+ and higher supported with c++14
    conflicts("%gcc@:4.8.99")

    def configure_args(self):
        args = []
        if '+sandboxing' not in self.spec:
            args.append('--disable-seccomp-sandboxing')
        if '+doc' not in self.spec:
            args.append('--disable-doc-gen')
        storedir = self.spec.variants['storedir'].value
        if storedir:
            args.append('--with-store-dir=' + storedir)
        statedir = self.spec.variants['statedir'].value
        if statedir:
            args.append('--localstatedir=' + statedir)
        return args

    @property
    def compiler_lib_dir(self):
        """
        :return: path where C++ standard library is located
        """
        if self.compiler.name != 'gcc':
            raise Exception('Unsupported compiler ' + self.compiler.name)
        bin_dir = osp.dirname(self.compiler.cxx)
        lib_dir = osp.normpath(osp.join(bin_dir, '..', 'lib64'))
        if not osp.isdir(lib_dir):
            raise Exception('Could not find compiler lib dir')
        libstdcpp = osp.join(lib_dir, 'libstdc++.so')
        if not osp.exists(libstdcpp):
            raise Exception('Could not find libstdc++ in lib dir' + lib_dir)
        return lib_dir

    def setup_environment(self, spack_env, run_env):
        if '+stdlibrpath' in self.spec:
            rpath_flag = self.compiler.cc_rpath_arg + '=' + self.compiler_lib_dir
            spack_env.append_flags('LDFLAGS', rpath_flag)
