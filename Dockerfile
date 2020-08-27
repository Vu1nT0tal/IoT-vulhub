# docker 安装 firmadyne

FROM ubuntu:18.04

WORKDIR /root

RUN apt update && apt upgrade -y 

RUN apt install -y wget python python-pip python-lzma busybox-static fakeroot git kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan p7zip-full && \
    git clone --recursive https://github.com/firmadyne/firmadyne.git

RUN	apt install -y git-core wget build-essential liblzma-dev liblzo2-dev zlib1g-dev unrar-free && \
    pip install -U pip

RUN git clone https://github.com/firmadyne/sasquatch && cd sasquatch && \
    make && make install && \
    cd .. && rm -rf sasquatch

RUN git clone https://github.com/ReFirmLabs/binwalk && cd binwalk && \
    ./deps.sh --yes && \
    python ./setup.py install && \
    pip install git+https://github.com/ahupp/python-magic && \
    pip install git+https://github.com/sviehb/jefferson && \
    cd .. && rm -rf binwalk

RUN	apt install -y qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils

RUN	cd ./firmadyne && ./download.sh && \
    sed -i  's/#FIRMWARE_DIR=\/home\/vagrant\/firmadyne/FIRMWARE_DIR=\/root\/firmadyne/g' firmadyne.config 

RUN apt install postgresql postgresql-client postgresql-contrib

USER postgres

RUN	cd /tmp && /etc/init.d/postgresql start && \
    psql --command "CREATE user firmadyne WITH PASSWORD 'firmadyne';" && \
    createdb -O firmadyne firmware && \
    psql -d firmware < /root/firmadyne/database/schema && \
    /etc/init.d/postgresql stop

USER root
ENV USER root
ENTRYPOINT su - postgres -c "/etc/init.d/postgresql start" && /bin/bash
