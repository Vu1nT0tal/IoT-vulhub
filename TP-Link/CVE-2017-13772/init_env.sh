#!/bin/bash

ARCH=${1}

cp ../../baseImage/busybox/1.31.0/busybox-${ARCH} ./system-emu/tools/busybox
cp ../../baseImage/gdbserver/7.11.1/${ARCH}-gdbserver ./system-emu/tools/gdbserver
cp ../../baseImage/msf/msf-${ARCH} ./system-emu/tools/msf
