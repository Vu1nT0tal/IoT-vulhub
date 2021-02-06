#!/bin/bash

cd buildroot-2020.02.6
cp /root/config/config_$1 ./.config
make toolchain
