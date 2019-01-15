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
from spack import *

class PyGrpcio(PythonPackage):
    """Package for gRPC Python"""

    homepage = "https://pypi.org/project/grpcio/"
    url      = "https://github.com/grpc/grpc/archive/v1.16.0.tar.gz"

    version('1.16.0', 'f7793df1c31a89a89d18966790c740b4')

    depends_on('cares',                    	type=('build', 'run'))
    depends_on('zlib',               		type=('build', 'run'))
    depends_on('openssl@1.0.2:',    		type=('build', 'run'))
    depends_on('py-setuptools',     		type='build')
    depends_on('py-six@1.10:',      		type=('build', 'run'))
    depends_on('py-futures@2.2.0:', 		type=('build', 'run'))
    depends_on('py-enum34@1.0.4:',  		type=('build', 'run'))
    depends_on('py-sphinx@1.3:',    		type=('build', 'run'))
    depends_on('py-sphinx-rtd-theme@0.1.8:', 	type=('build', 'run'))
    depends_on('py-cython@0.23:',         	type=('build', 'run'))

    def setup_environment(self, spack_env, run_env):
        spack_env.set('GRPC_PYTHON_BUILD_WITH_CYTHON', '1')
        spack_env.set('GRPC_PYTHON_BUILD_SYSTEM_OPENSSL', '1')
        spack_env.set('GRPC_PYTHON_BUILD_SYSTEM_ZLIB', '1')
        spack_env.set('GRPC_PYTHON_BUILD_SYSTEM_CARES', '1')
        spack_env.append_flags('LDFLAGS', self.spec['cares'].libs.search_flags)
        spack_env.append_flags('LDFLAGS', self.spec['zlib'].libs.search_flags)
