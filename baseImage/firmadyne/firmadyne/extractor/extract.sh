#! /bin/bash

infile=$1
outdir=$2

# override 65535k docker default size with tmpfs default
mem=$(($(free | awk '/^Mem:/{print $2}') / 2))k

indir=$(realpath $(dirname "${infile}"))
outdir=$(realpath "${outdir}")
infilebn=$(basename "${infile}")

docker run --rm -t -i --tmpfs /tmp:rw,size=${mem} \
  -v "${indir}":/firmware-in:ro \
  -v "${outdir}":/firmware-out \
  "ddcc/firmadyne-extractor:latest" \
  fakeroot /home/extractor/extractor/extractor.py \
  -np \
  /firmware-in/"${infilebn}" \
  /firmware-out
