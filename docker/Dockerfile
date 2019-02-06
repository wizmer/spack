FROM ubuntu:18.04
MAINTAINER Pramod Kumbhar <pramod.s.kumbhar@gmail.com>
MAINTAINER Matthias Wolf <matthias.wolf@epfl.ch>

ENV DEBIAN_FRONTEND noninteractive

ARG proxy
ENV http_proxy=$proxy
ENV https_proxy=$proxy

# default software required
RUN apt-get update
RUN apt-get -y install software-properties-common
RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt-get update
RUN apt-get -y \
            --allow-downgrades \
            --allow-remove-essential \
            --allow-change-held-packages \
            install \
                autoconf \
                automake \
                bison \
                build-essential \
                cmake \
                curl \
                cython \
                diffutils \
                flex \
                gfortran \
                git \
                libboost-all-dev \
                libbz2-dev \
                libhdf5-serial-dev \
                libncurses-dev \
                libpciaccess-dev \
                libopenmpi-dev \
                libreadline-dev \
                libtool \
                libxml2-dev \
                make \
                numactl \
                pkg-config \
                python2.7-dev \
                python-minimal \
                python-numpy \
                software-properties-common \
                tcl-dev \
                unzip \
                vim \
                zlib1g-dev

RUN git clone https://github.com/BlueBrain/spack.git
ENV SPACK_ROOT $PWD/spack
ENV PATH $SPACK_ROOT/bin:$PATH

# see this: http://stackoverflow.com/questions/20635472/using-the-run-instruction-in-a-dockerfile-with-source-does-not-work
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN . $SPACK_ROOT/share/spack/setup-env.sh
RUN echo ". $SPACK_ROOT/share/spack/setup-env.sh" \
    > /etc/profile.d/spack.sh

RUN spack compiler find && spack compilers

RUN mkdir -p $SPACK_ROOT/etc/spack
ADD packages.yaml $SPACK_ROOT/etc/spack
ADD modules.yaml $SPACK_ROOT/etc/spack
ADD config.yaml $SPACK_ROOT/etc/spack

RUN ssh-keyscan github.com >> /etc/ssh/known_hosts

WORKDIR "/spack"
RUN git fetch

ARG pr
RUN [[ "x$pr" != "x" ]] && git fetch +refs/pull/$pr/head:refs/remotes/origin/pull/$pr

ARG revision=develop
RUN git checkout $revision
