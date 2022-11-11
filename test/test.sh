#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR=$(realpath ${0%/*})
cd $SCRIPT_DIR

if [[ ! -d ../.venv ]]; then
  cd ..
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install -e .
  cd test
else
  cd ..
  source .venv/bin/activate
  cd test
fi

python3 -m pytest test.py
deactivate
