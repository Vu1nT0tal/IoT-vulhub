#!/bin/sh

set -e
sudo apt update
sudo apt install -y python-pip python3-pip unzip busybox-static git dmsetup nmap fakeroot netcat-openbsd python-psycopg2 pytho3-psycopg2 kpartx snmp uml-utilities util-linux vlan qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils

echo "Installing binwalk"
git clone --depth=1 https://github.com/ReFirmLabs/binwalk
cd binwalk
sudo ./deps.sh
sudo python3 ./setup.py install
sudo -H pip3 install git+https://github.com/ahupp/python-magic
sudo -H pip install git+https://github.com/sviehb/jefferson
cd ..

echo "Installing firmadyne"
firmadyne_dir=$(realpath .)

# Set FIRMWARE_DIR in firmadyne.config
sed -i "/FIRMWARE_DIR=/c\FIRMWARE_DIR=$firmadyne_dir" firmadyne.config
cd ..

echo "Firmadyne installed successfully!"
