#!/usr/bin/env bash

# check argument
if [ "$#" -ge 1 ]; then
    if [ "$2" == "-v" ]; then
        VERB=true
    else
    	VERB=false
    fi
else
    echo "Please specify a firmware file as first argument"
    echo "Example: ./auto_launch.sh Router-firmware.zip"
    exit 1
fi

# check file existence
if [ ! -f ${1} ]; then
    echo "Input file not found: ${1}"
    exit 1
fi
FNAME=$(basename -- "${1}")
FNAME="${FNAME%.*}"

# check the images ID counter
re="^[0-9]+$"
ID=$(ls images/ | sort -n | tail -1 | cut -d '.' -f1)
if ! [[ ${ID} =~ ${re} ]] ; then
    ID="0"
fi
ID=$((ID + 1))

# launch the extractor
echo 'Extracting the firmware...'
if ${VERB} ; then
    ./sources/extractor/extractor.py -np -nk "${1}" images
else
    ./sources/extractor/extractor.py -np -nk "${1}" images > /dev/null 2>&1
fi

# choose an appropriate ID for the extracted fs
FILE=$(ls images | grep -F "${FNAME}") && mv images/"${FILE}" images/${ID}.tar.gz

# check file existence
if [ ! -f ./images/${ID}.tar.gz ]; then
    echo "File ./images/${ID}.tar.gz not found, probably an extraction problem happened"
    exit 1
fi

# get the architecture
echo 'Getting the architecture...'
ARCH=$(./scripts/getArch.sh ./images/${ID}.tar.gz | cut -d ' ' -f2)

# create the image and get network info
echo 'Creating the image...'
if ${VERB} ; then
    sudo ./scripts/makeImage.sh ${ID} ${ARCH}
    sudo ./scripts/inferNetwork.sh ${ID} ${ARCH}
else
    sudo ./scripts/makeImage.sh ${ID} ${ARCH} > /dev/null 2>&1
    sudo ./scripts/inferNetwork.sh ${ID} ${ARCH} > /dev/null 2>&1
fi

# run the emulation
sudo ./scratch/${ID}/run.sh

# cleanup
echo 'Cleaning up...'
rm images/${ID}.tar.gz
sudo rm -rf scratch/${ID}
