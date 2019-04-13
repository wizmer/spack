# Copyright 2013-2019 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *
from glob import glob
import os


class Tensorflow(Package):
    """TensorFlow is an Open Source Software Library for Machine Intelligence"""

    homepage = "https://www.tensorflow.org"
    url      = "https://github.com/tensorflow/tensorflow/archive/v0.10.0.tar.gz"

    version('1.13.1',    sha256='7cd19978e6bc7edc2c847bce19f95515a742b34ea5e28e4389dade35348f58ed')
    version('1.12.0',    '48164180a2573e75f1c8dff492a550a0', preferred=True)
    version('1.9.0',     '3426192cce0f8e070b2010e5bd5695cd')
    version('1.8.0',     'cd45874be9296644471dd43e7da3fbd0')
    version('1.6.0',     '6dc60ac37e49427cd7069968da42c1ac')
    version('1.5.0',     'e087dc1f47dbbda87cf4278acddf785b')
    version('1.3.0',     '01c008c58d206324ef68cd5116a83965')
    version('1.2.0',     '3f15746caabfd2583724258643fd1678')
    version('1.1.0',     'fb745649d33954c97d29b7acaffe7d65')
    version('0.10.0',    'b75cbd494d61a809af5ef25d7fba561b')

    depends_on('swig',                          type='build')

    # old tensorflow needs old bazel
    depends_on('bazel@0.15.0',                  type='build',          when='@1.12.0:')
    depends_on('bazel@0.10.0',                  type='build',          when='@1.8.0:1.9.0')
    depends_on('bazel@0.9.0',                   type='build',          when='@1.5.0:1.6.0')
    depends_on('bazel@0.4.5',                   type='build',          when='@1.2.0:1.3.0')
    depends_on('bazel@0.4.4:0.4.999',           type='build',          when='@1.0.0:1.1.0')
    depends_on('bazel@0.3.1:0.4.999',           type='build',          when='@:1.0.0')

    extends('python')
    depends_on('py-setuptools',                 type=('build', 'run'))
    depends_on('py-numpy@1.11.0:',              type=('build', 'run'))
    depends_on('py-six@1.10.0:',                type=('build', 'run'))

    depends_on('py-protobuf@3.6.1',             type=('build', 'run'), when='@1.8.0:')
    depends_on('py-protobuf@3.3.0:',            type=('build', 'run'), when='@1.3.0:1.6.0')
    depends_on('py-protobuf@3.0.0b2',           type=('build', 'run'), when='@:1.2.0')

    depends_on('py-wheel',                      type=('build', 'run'))
    depends_on('py-mock@2.0.0:',                type=('build', 'run'))

    depends_on('py-enum34@1.1.6:',              type=('build', 'run'), when='@1.5.0:^python@:3.3.99')
    depends_on('py-absl-py@0.1.6',              type=('build', 'run'), when='@1.5.0:')

    depends_on('py-astor@0.1.6:',               type=('build', 'run'), when='@1.6.0:')
    depends_on('py-gast@0.2.0:',                type=('build', 'run'), when='@1.6.0:')
    depends_on('py-grpcio@1.8.6:',              type=('build', 'run'), when='@1.6.0:')
    depends_on('py-termcolor@1.1.0:',           type=('build', 'run'), when='@1.6.0:')

    depends_on('py-keras-applications@1.0.6:',  type=('build', 'run'), when='@1.12.0:')
    depends_on('py-keras-preprocessing@1.0.5:', type=('build', 'run'), when='@1.12.0:')
    depends_on('py-h5py',                       type=('build', 'run'), when='@1.12.0:')

    patch('url-zlib.patch',  when='@0.10.0')

    variant('gcp', default=False,
            description='Enable Google Cloud Platform Support')

    variant('cuda', default=False,
            description='Enable CUDA Support')

    depends_on('cuda', when='+cuda')
    depends_on('cudnn', when='+cuda')
    depends_on('nccl', when='+cuda')


    def install(self, spec, prefix):
        if '+gcp' in spec:
            env['TF_NEED_GCP'] = '1'
        else:
            env['TF_NEED_GCP'] = '0'

        env['PYTHON_BIN_PATH'] = str(spec['python'].prefix.bin) + '/python'
        env['PYTHONUSERBASE'] = str(spec['python'].prefix)
        env['USE_DEFAULT_PYTHON_LIB_PATH'] = '1'
        env['SWIG_PATH'] = str(spec['swig'].prefix.bin)
        env['GCC_HOST_COMPILER_PATH'] = spack_cc

        env['TF_ENABLE_XLA'] = '0'

        if '+cuda' in spec:
            env['TF_NEED_CUDA'] = '1'
            env['TF_CUDA_CLANG'] = '0'
            env['TF_NEED_TENSORRT'] = '0'
            env['TF_CUDA_VERSION'] = str(spec['cuda'].version)
            env['CUDA_TOOLKIT_PATH'] = str(spec['cuda'].prefix)
            env['TF_CUDNN_VERSION'] = str(spec['cudnn'].version)[0]
            env['CUDNN_INSTALL_PATH'] = str(spec['cudnn'].prefix)
            env['NCCL_INSTALL_PATH'] = str(spec['nccl'].prefix)
            env['TF_NCCL_VERSION'] = str(spec['nccl'].version)[0]
            env['TF_CUDA_COMPUTE_CAPABILITIES'] = '6.0,6.1,7.0'
        else:
            env['TF_NEED_CUDA'] = '0'
            env['TF_CUDA_VERSION'] = ''
            env['CUDA_TOOLKIT_PATH'] = ''
            env['TF_CUDNN_VERSION'] = ''
            env['CUDNN_INSTALL_PATH'] = ''

        # additional config options starting with version 1.2
        if self.spec.satisfies('@1.2.0:'):
            env['TF_NEED_MKL'] = '1'
            env['TF_NEED_VERBS'] = '1'

        # additional config options starting with version 1.3
        if self.spec.satisfies('@1.3.0:'):
            env['TF_NEED_MPI'] = '0'

        # additional config options starting with version 1.5
        if self.spec.satisfies('@1.5.0:'):
            env['TF_NEED_S3'] = '0'
            env['TF_NEED_GDR'] = '0'
            env['TF_NEED_OPENCL_SYCL'] = '0'
            env['TF_SET_ANDROID_WORKSPACE'] = '0'
            # env variable is somehow ignored -> brute force
            filter_file(r'if workspace_has_any_android_rule\(\)', r'if True', 'configure.py')

        # additional config options starting with version 1.6
        if self.spec.satisfies('@1.6.0:'):
            env['TF_NEED_KAFKA'] = '0'

        # additional config options starting with version 1.8
        if self.spec.satisfies('@1.8.0:'):
            env['TF_DOWNLOAD_CLANG'] = '0'
            env['TF_NEED_AWS'] = '0'

        # boringssl error again, build against openssl instead via TF_SYSTEM_LIBS
        # does not work for tf < 1.12.0
        # (https://github.com/tensorflow/tensorflow/issues/25283#issuecomment-460124556)
        if self.spec.satisfies('@1.12.0:'):
            env['TF_SYSTEM_LIBS'] = "boringssl"
            env['TF_NEED_IGNITE'] = '0'
            env['TF_NEED_ROCM'] = '0'

        # set tmpdir to a non-NFS filesystem (because bazel uses ~/.cache/bazel)
        # TODO: This should be checked for non-nfsy filesystem, but the current
        #       best idea for it is to check
        #           subprocess.call(['stat', '--file-system', '--format=%T', tmp_path])
        #       to not be nfs. This is only valid for Linux and we'd like to
        #       stay at least also OSX compatible
        # Note: This particular path below /tmp/spack/tmp is required by the visionary container
        #       build flow:
        # Note: On BB5 if we use /tmp as TMPDIR then we get "java.io.IOException: No space left on device"
        # tmp_path = env.get('SPACK_TMPDIR', '/tmp/spack') + '/tf'
        # mkdirp(tmp_path)
        # env['TEST_TMPDIR'] = tmp_path
        # env['HOME'] = tmp_path

        configure()


        # version dependent fixes
        if self.spec.satisfies('@1.3.0:1.5.0'):
            # checksum for protobuf that bazel downloads (@github) changed, comment out to avoid error
            # better solution: replace wrong checksums in workspace.bzl
            # wrong one: 6d43b9d223ce09e5d4ce8b0060cb8a7513577a35a64c7e3dad10f0703bf3ad93,
            # online: e5fdeee6b28cf6c38d61243adff06628baa434a22b5ebb7432d2a7fbabbdb13d
            filter_file(r'sha256 = "6d43b9d223ce09e5d4ce8b0060cb8a7513577a35a64c7e3dad10f0703bf3ad93"',
                        r'#sha256 = "6d43b9d223ce09e5d4ce8b0060cb8a7513577a35a64c7e3dad10f0703bf3ad93"',
                        'tensorflow/workspace.bzl')
            # starting with tensorflow 1.3, tensorboard becomes a dependency
            # (...but is not really needed? Tensorboard should depend on tensorflow, not the other way!)
            # -> remove from list of required packages
            filter_file(r"'tensorflow-tensorboard",
                        r"#'tensorflow-tensorboard",
                        'tensorflow/tools/pip_package/setup.py')
        if self.spec.satisfies('@1.5.0:'):
            # google cloud support seems to be installed on default, leading to boringssl error
            # manually set the flag to false to avoid installing gcp support
            # (https://github.com/tensorflow/tensorflow/issues/20677#issuecomment-404634519)
            filter_file(r'--define with_gcp_support=true',
                        r'--define with_gcp_support=false',
                        '.tf_configure.bazelrc')
        if self.spec.satisfies('@1.6.0:'):
            # tensorboard name changed
            filter_file(r"'tensorboard >=",
                        r"#'tensorboard >=",
                        'tensorflow/tools/pip_package/setup.py')
        if self.spec.satisfies('@1.8.0:'):
            # 1.8.0 and 1.9.0 aborts with numpy import error during python_api generation
            # somehow the wrong PYTHONPATH is used...set --distinct_host_configuration=false as a workaround
            # (https://github.com/tensorflow/tensorflow/issues/22395#issuecomment-431229451)
            filter_file('build --action_env TF_NEED_OPENCL_SYCL="0"',
                        'build --action_env TF_NEED_OPENCL_SYCL="0"\n'
                        'build --distinct_host_configuration=false\n'
                        'build --action_env PYTHONPATH="{}"'.format(env['PYTHONPATH']),
                        '.tf_configure.bazelrc')

        if self.spec.satisfies('@1.12.0:'):
            # add link to spack-installed openssl libs (needed if no system openssl available)
            filter_file('-lssl', '-lssl '+self.spec['openssl'].libs.search_flags, 'third_party/systemlibs/boringssl.BUILD')
            filter_file('-lcrypto', '-lcrypto '+self.spec['openssl'].libs.search_flags, 'third_party/systemlibs/boringssl.BUILD')

        if '+cuda' in spec:
            # get path for all dependent libraries to avoid issue with linking esp cudnn
            # ld_lib_path = env.get('LD_LIBRARY_PATH')
            # bazel('-c', 'opt', '--config=cuda', '--action_env="LD_LIBRARY_PATH=%s"' % ld_lib_path,  '//tensorflow/tools/pip_package:build_pip_package')
            bazel('-c', 'opt', '--config=cuda',  '//tensorflow/tools/pip_package:build_pip_package')
        else:
            bazel('-c', 'opt', '--config=mkl', '//tensorflow/tools/pip_package:build_pip_package')

        build_pip_package = Executable('bazel-bin/tensorflow/tools/pip_package/build_pip_package')
        build_pip_package('.')

        # using setup.py for installation
        # webpage suggests: sudo pip install /tmp/tensorflow_pkg/tensorflow-0.XYZ.whl
        mkdirp('_python_build')
        cd('_python_build')
        ln = which('ln')

        for fn in glob("../bazel-bin/tensorflow/tools/pip_package/build_pip_package.runfiles/org_tensorflow/*"):
            ln('-s', fn, '.')
        for fn in glob("../tensorflow/tools/pip_package/*"):
            ln('-s', fn, '.')
        setup_py('install', '--prefix={0}'.format(prefix))

    def setup_environment(self, spack_env, run_env):
        # Note : do not enable skylake yet, see https://github.com/easybuilders/easybuild-easyconfigs/issues/5936
        opt_flags = "--copt=-mavx --copt=-mavx2 --copt=-mfma --copt=-msse4.2 --copt=-mfpmath=both"
        spack_env.set('CC_OPT_FLAGS', opt_flags)
