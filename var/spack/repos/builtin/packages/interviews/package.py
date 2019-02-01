# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Interviews(AutotoolsPackage):
    """GUI package for NEURON Simulator"""

    homepage = "https://www.neuron.yale.edu/"
    url      = "https://neuron.yale.edu/ftp/neuron/versions/v7.6/iv-19.tar.gz"

    version('19', '4ffb44b21c67f1126128953f349e24e4')

    depends_on("libxcomposite")
    depends_on('libxext')
    depends_on('libx11')

    def configure_args(self):
        spec = self.spec
        return [
            '--with-x',
            '--x-includes={0}'.format(spec['libx11'].prefix.include),
            '--x-libraries={0}'.format(spec['libx11'].prefix.lib),
        ]
