# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyNeuroc(PythonPackage):
    """Python library neuron morphology analysis"""

    homepage = "https://github.com/BlueBrain/NeuroM"
    url = "https://pypi.io/packages/source/n/neurom/neurom-1.4.10.tar.gz"

    version('0.1.5', tag='v0.1.5')
    version('0.1.1', sha256='e541f6c8a11826caa2b2d1cf18015a10ec7009f12813edfc2655084c7cf5021b')

    depends_on('py-click@7.0:', type='run')
    depends_on('py-future@0.16.0:', type='run')
    depends_on('py-neurom@1.4.14:', type='run')
    depends_on('py-tqdm@4.8.4:', type='run')
