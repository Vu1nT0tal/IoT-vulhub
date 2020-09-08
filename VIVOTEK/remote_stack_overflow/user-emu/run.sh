#!/bin/bash

cd ./squashfs-root
mount -o bind /dev ./dev
mount -t proc /proc ./proc
echo "127.0.0.1 `hostname` localhost" > ./etc/hosts
chroot . ./qemu-arm-static ./usr/sbin/httpd

while true; do sleep 100; done
