# docker 安装 firmadyne

FROM firmianay/binwalk:noentry

WORKDIR /root

COPY ./firmadyne /root/firmadyne

RUN apt-get update && \
    apt-get install -y python-lzma busybox-static kpartx netcat nmap snmp uml-utilities util-linux vlan p7zip-full && \
    apt-get install -y wget build-essential liblzma-dev liblzo2-dev zlib1g-dev unrar-free && \
    apt-get install -y qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils && \
    pip3 install python-magic && rm -rf /var/lib/apt/lists/*

#RUN git clone --depth=1 https://github.com/ReFirmLabs/binwalk && cd binwalk && \
#    sed -i 's/devttys0\/sasquatch/firmianay\/sasquatch -b patch-1/g' deps.sh && \
#    ./deps.sh --yes && \
#    python3 ./setup.py install && \
#    pip3 install python-magic && \
#    cd .. && rm -rf binwalk && rm -rf /var/lib/apt/lists/*
