#!/bin/bash

cwd=$(dirname $0)

export PYTHONPATH="${cwd}/src:${cwd}/../pyoidc/src"
export PATH="${cwd}/script:${PATH}"

$@
