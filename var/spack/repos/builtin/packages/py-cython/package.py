# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
import os

class PyCython(PythonPackage):
    """The Cython compiler for writing C extensions for the Python language."""
    homepage = "https://pypi.python.org/pypi/cython"
    url      = "https://pypi.io/packages/source/c/cython/Cython-0.25.2.tar.gz"

    version('0.29', sha256='94916d1ede67682638d3cc0feb10648ff14dc51fb7a7f147f4fedce78eaaea97')
    version('0.28.6', '3c3fb47806a4476f8e9429943439cc60')
    version('0.28.3', '586f0eb70ba1fcc34334e9e10c5e68c0')
    version('0.28.1', 'c549effadb52d90bdcb1affc1e5dbb97')
    version('0.25.2', '642c81285e1bb833b14ab3f439964086')
    version('0.23.5', '66b62989a67c55af016c916da36e7514')
    version('0.23.4', '157df1f69bcec6b56fd97e0f2e057f6e')

    # These versions contain illegal Python3 code...
    version('0.22', '1ae25add4ef7b63ee9b4af697300d6b6')
    version('0.21.2', 'd21adb870c75680dc857cd05d41046a4')

    @property
    def command(self):
        """Returns the Cython command"""
        return Executable(self.prefix.bin.cython)

    def setup_environment(self, spack_env, run_env):
	if self.spec.satisfies('%intel'):
            spack_env.set('LDSHARED', '%s -shared' % spack_cc)
