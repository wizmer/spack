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

class PyKerasApplications(PythonPackage):
    """
    Keras Applications is the applications module of the Keras deep learning
    library.  It provides model definitions and pre-trained weights for a
    number of popular archictures, such as VGG16, ResNet50, Xception,
    MobileNet, and more.
    """

    homepage = "https://github.com/keras-team/keras-applications"
    url      = "https://github.com/keras-team/keras-applications/archive/1.0.6.tar.gz"

    version('1.0.6', 'ae4926c3d973da42c68320372aa4b63c')

    depends_on('py-setuptools', type='build')
    depends_on('py-numpy@1.9.1:', type=('build', 'run'))
    depends_on('py-h5py', type=('build', 'run'))
