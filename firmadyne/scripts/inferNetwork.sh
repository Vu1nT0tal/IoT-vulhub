#!/bin/bash

set -e
set -u

if [ -e ./firmadyne.config ]; then
    source ./firmadyne.config
elif [ -e ../firmadyne.config ]; then
    source ../firmadyne.config
else
    echo "Error: Could not find 'firmadyne.config'!"
    exit 1
fi

if check_number $1; then
    echo "Usage: inferNetwork.sh <image ID> [<architecture>]"
    exit 1
fi
IID=${1}

if check_arch "${2}"; then
    echo "Error: Invalid architecture!"
    exit 1
fi

ARCH=${2}

echo "Running firmware ${IID}: terminating after 60 secs..."
timeout --preserve-status --signal SIGINT 60 "${SCRIPT_DIR}/run.${ARCH}.sh" "${IID}"
sleep 1

echo "Inferring network..."
"${SCRIPT_DIR}/makeNetwork.py" -i "${IID}" -q -o -a "${ARCH}" -S "${SCRATCH_DIR}"

echo "Done!"
