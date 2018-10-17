#!/bin/bash

packages=(
    'neuronmodels@ring'
    'neuronmodels@bbp'
    'neuronmodels@traub'
)

for variant in "~profile" "+profile"
do
    for package in "${packages[@]}"
    do
        echo "Installing package $package $variant"
        spack spec -I $package $variant
        spack install -n $package $variant
    done
done
