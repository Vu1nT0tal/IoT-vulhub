FROM ubuntu:16.04
LABEL Author="firmianay@gmail.com"

WORKDIR /root

RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends python python-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 binwalk
RUN apt-get update \
    && apt-get install -y --no-install-recommends git wget unzip python \
    && wget -q --tries=0 https://github.com/ReFirmLabs/binwalk/archive/master.zip && unzip -q master.zip \
    # && git clone --depth=1 https://github.com/ReFirmLabs/binwalk.git \
    && cd binwalk-master && ./deps.sh --yes && python ./setup.py install \
    && cd .. && rm -rf binwalk-master master.zip \
    && apt-get purge -y --autoremove git wget unzip \
    && rm -rf /var/lib/apt/lists/*

# 解压固件
COPY ./firmware /root
RUN binwalk -Me ./firmware/* \
    && cp -r ./firmware/_*/_31*/_root*/squashfs-root ./ \
    && rm -rf ./squashfs-root/etc && cp -r ./firmware/_*/_31*/defconf/_*/_*/etc ./squashfs-root \
    && echo "127.0.0.1 `hostname` localhost" > ./squashfs-root/etc/hosts \
    && rm -rf ./firmware

# 安装 qemu-user-static
RUN apt-get install -y –-no-install-recommends qemu-user-static \
    && cp cp /usr/bin/qemu-arm-static ./squashfs-root \
    && apt-get purge -y --autoremove qemu-user-static \
    && rm -rf /var/lib/apt/lists/*

## 启动 httpd
RUN cd ./squashfs-root \
    && mount -o bind /dev ./dev \
    && mount -t proc /proc ./proc \
    && chroot . ./qemu-arm-static ./usr/sbin/httpd &
