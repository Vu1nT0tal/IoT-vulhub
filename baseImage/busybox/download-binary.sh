#!/bin/bash

version="$1"

if [ ! -d $version ]; then
  mkdir $version
fi

wget -P ./$version https://busybox.net/downloads/binaries/$version-defconfig-multiarch-musl/busybox-armv5l
wget -P ./$version https://busybox.net/downloads/binaries/$version-defconfig-multiarch-musl/busybox-mips
wget -P ./$version https://busybox.net/downloads/binaries/$version-defconfig-multiarch-musl/busybox-mipsel
