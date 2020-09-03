# docker 安装 firmadyne

FROM ubuntu:16.04

WORKDIR /root

RUN apt update && apt upgrade -y && \
    apt install -y wget python python-pip python-lzma busybox-static fakeroot git kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan p7zip-full && \
    rm -rf /var/lib/apt/lists/*

RUN	apt install -y git-core wget build-essential liblzma-dev liblzo2-dev zlib1g-dev unrar-free && \
    pip install -U pip && \
    apt install -y qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ReFirmLabs/binwalk && cd binwalk && \
    ./deps.sh --yes && \
    python ./setup.py install && \
    cd .. && rm -rf binwalk

RUN	git clone --recursive https://github.com/firmadyne/firmadyne.git && \
    cd ./firmadyne && ./download.sh && \
    sed -i  's/#FIRMWARE_DIR=\/home\/vagrant\/firmadyne/FIRMWARE_DIR=\/root\/firmadyne/g' firmadyne.config 

RUN apt install postgresql postgresql-client postgresql-contrib && \
    rm -rf /var/lib/apt/lists/*

USER postgres

RUN	cd /tmp && /etc/init.d/postgresql start && \
    psql --command "CREATE user firmadyne WITH PASSWORD 'firmadyne';" && \
    createdb -O firmadyne firmware && \
    psql -d firmware < /root/firmadyne/database/schema && \
    /etc/init.d/postgresql stop

USER root
ENV USER root
ENTRYPOINT su - postgres -c "/etc/init.d/postgresql start" && /bin/bash
