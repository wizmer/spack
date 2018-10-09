##############################################################################
# Copyright (c) 2017, Los Alamos National Security, LLC
# Produced at the Los Alamos National Laboratory.
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

class Neuronmodelresource(Package):
    """MOD and HOC file resources used by Neuronmodel package"""

    homepage = "https://github.com/pramodk/neuronmodels"
    url      = "https://github.com/pramodk/neuronmodels.git"

    version('develop', git=url, preferred=True)

    resource(
        name='ring',
        git='https://github.com/pramodk/ringtest.git',
        branch='master',
        placement='ring',
        destination='models'
    )
    resource(
        name='traub',
        git='https://github.com/pramodk/nrntraub.git',
        branch='icei',
        placement='traub',
        destination='models'
    )
    resource(
        name='coretest',
        git='https://github.com/pramodk/testcorenrn.git',
        branch='master',
        placement='coretest',
        destination='models'
    )

    def install(self, spec, prefix):
        shutil.copytree('models', '%s/models' % (prefix), symlinks=False)

    def setup_dependent_package(self, module, dependent_spec):
        model_dir = '%s/models/%s' % (self.spec.prefix, dependent_spec.version)
        python_path =  model_dir
        hoc_path = model_dir
        if os.path.isdir('%s/hoc' % model_dir):
            hoc_path += ':%s/hoc' % model_dir
        dependent_spec.package.hoc_path = hoc_path
        dependent_spec.package.python_path = python_path
