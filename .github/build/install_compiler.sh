#!/bin/bash

if [ $# -ne 1 ];then
    echo "Missing arch"
    exit 1
fi

ARCH="${1,,}"
case $ARCH in
    x86_64|i686|aarch64)
        ARCH="${ARCH}-linux-musl"
        ;;
    x86)
        ARCH="i686-linux-musl"
        ;;
    arm)
        ARCH="arm-linux-musleabihf"
        ;;
    *)
        echo "Invalid arch ${ARCH}"
        exit 1
        ;;
esac

cd /

HOST="http://musl.cc"
curl -so ${ARCH}-cross.tgz ${HOST}/${ARCH}-cross.tgz
tar -xf ${ARCH}-cross.tgz 
rm ${ARCH}-cross.tgz
