#!/usr/bin/env bash

# This file is used to set up the bats-assert and bats-support libraries for testing

# Get the directory of this script
CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LIB_DIR="${CURR_DIR}/lib"

# Clone the libraries if they don't exist
if [ ! -d "${LIB_DIR}/bats-support" ]; then
  echo "Cloning bats-support..."
  git clone https://github.com/bats-core/bats-support "${LIB_DIR}/bats-support"
fi

if [ ! -d "${LIB_DIR}/bats-assert" ]; then
  echo "Cloning bats-assert..."
  git clone https://github.com/bats-core/bats-assert "${LIB_DIR}/bats-assert"
fi

echo "Bats libraries are ready to use."
