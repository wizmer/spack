# Setup for BlueBrain5

On BlueBrain5, clone this repository to get started using Spack.
The following commands are a good way to get started:

    $ git clone https://github.com/BlueBrain/spack.git
    $ . spack/share/spack/setup-env.sh
    $ ln -s /gpfs/bbp.cscs.ch/apps/hpc/jenkins/config/*.yaml ${SPACK_ROOT}/etc/spack

This will install all software into the directory that Spack was cloned
into.
The configuration linked into the `etc/spack` subdirectory will provide a
setup to re-use centrally installed software and decrease installation
times.

To use multiple different software directories, one can override the
configuration above by creating a `${HOME}/.spack/config.yaml` with the
following contents:
```yaml
config:
  install_tree:
    root: $SPACK_INSTALL_PREFIX
  source_cache: $SPACK_INSTALL_PREFIX/.cache
  module_roots:
    tcl: $SPACK_INSTALL_PREFIX/modules/tcl
    lmod: $SPACK_INSTALL_PREFIX/modules/lmod
```
and then exporting the environment variable `${SPACK_INSTALL_PREFIX}` to
point to a location where the software should be located.

Similarly, the module configuration can be overwritten to provide modules
for **all** manually installed software, including new dependencies, by
creating the file `${HOME}/.spack/modules.yaml` with the following
contents:
```yaml
modules:
  tcl:
    whitelist:
      - '@:'
    projections:
      all: '{name}/{version}-{hash:6}'
```