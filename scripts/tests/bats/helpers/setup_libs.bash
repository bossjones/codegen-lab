#!/usr/bin/env bash

# This file is used to set up the bats-assert and bats-support libraries for testing

# Get the directory of this script
CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
LIB_DIR="${CURR_DIR}/lib"
export BATS_LIB_PATH=${BATS_LIB_PATH:-"${LIB_DIR}"}

echo "BATS_LIB_PATH: ${BATS_LIB_PATH}"

# Clone the libraries if they don't exist
if [ ! -d "${BATS_LIB_PATH}/bats-support" ]; then
  echo "Cloning bats-support..."
  git clone https://github.com/bats-core/bats-support "${BATS_LIB_PATH}/bats-support"
fi

if [ ! -d "${BATS_LIB_PATH}/bats-assert" ]; then
  echo "Cloning bats-assert..."
  git clone https://github.com/bats-core/bats-assert "${BATS_LIB_PATH}/bats-assert"
fi

if [ ! -d "${BATS_LIB_PATH}/bats-file" ]; then
  echo "Cloning bats-file..."
  git clone https://github.com/bats-core/bats-file "${BATS_LIB_PATH}/bats-file"
fi

echo "Bats libraries are ready to use."
