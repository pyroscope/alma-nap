#!/usr/bin/env bash
#
# Set up work / development environment

set -e
ROOTDIR=$(command cd $(dirname "$0") && pwd)
PROJECT=$(basename "$ROOTDIR")

fail() {
    echo >&2 "ERROR:" "$@"
    exit 1
}

# Create virtualenv and install Python tools
venv_bin="/usr/bin/virtualenv"
[[ -x "$venv_bin" ]] || fail "You need to 'apt-get install python-virtualenv' or similar!"
mkdir -p .pyvenv
if [[ ! -x .pyvenv/$PROJECT/bin/python ]]; then
    test ! -d .pyvenv/$PROJECT || rm -rf .pyvenv/$PROJECT
    "$venv_bin" .pyvenv/$PROJECT
fi
if [[ ! -x .pyvenv/$PROJECT/bin/invoke ]]; then
    for pypkg in pip setuptools wheel "requests[security]"; do
        .pyvenv/$PROJECT/bin/pip install -U "$pypkg"
    done
    .pyvenv/$PROJECT/bin/pip install -r requirements.txt
fi

# Delegate further setup work to Invoke task
.pyvenv/$PROJECT/bin/invoke _bootstrap

echo
echo "Call '. .env' to activate tools, or install 'https://github.com/kennethreitz/autoenv'!"
