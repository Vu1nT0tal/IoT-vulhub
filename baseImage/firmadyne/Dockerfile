# docker 安装 firmadyne

FROM firmianay/ubuntu:16.04

WORKDIR /root

COPY ./firmadyne /root/firmadyne

RUN apt-get update && \
    apt-get install -y python-lzma busybox-static fakeroot git kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan p7zip-full && \
    apt-get install -y wget build-essential liblzma-dev liblzo2-dev zlib1g-dev unrar-free && \
    apt-get install -y qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ReFirmLabs/binwalk && cd binwalk && \
    ./deps.sh --yes && \
    python ./setup.py install && \
    cd .. && rm -rf binwalk

RUN	cd /root/firmadyne \
    sed -i  's/#FIRMWARE_DIR=\/home\/vagrant\/firmadyne/FIRMWARE_DIR=\/root\/firmadyne/g' firmadyne.config 

ENTRYPOINT ["/bin/bash"]
