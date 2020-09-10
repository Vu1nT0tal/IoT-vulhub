#!/bin/bash

version="$1"

if [ ! -d $version ]; then
  mkdir $version
fi

wget -P ./$version https://busybox.net/downloads/busybox-$version.tar.bz2
