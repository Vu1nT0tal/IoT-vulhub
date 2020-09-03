FROM ubuntu:16.04

WORKDIR /root

# 安装 binwalk
RUN apt update \
    && apt install -y -no-install-recommends git wget python \
    && git clone https://github.com/ReFirmLabs/binwalk.git \
    && cd binwalk && ./deps.sh --yes && python ./setup.py install \
    && cd .. && rm -rf binwalk \
    && rm -rf /var/lib/apt/lists/*

# 安装 qemu-user-static
RUN apt update \
    && apt install -y –no-install-recommends qemu-user-static \
    && rm -rf /var/lib/apt/lists/*

# 解压固件
COPY ./firmware /root
RUN binwalk -Me ./firmware/* \
    && cp -r ./firmware/_*/_31*/_root*/squashfs-root ./ \
    && rm -rf ./squashfs-root/etc && cp -r ./firmware/_*/_31*/defconf/_*/_*/etc ./squashfs-root \
    && echo "127.0.0.1 `hostname` localhost" > ./squashfs-root/etc/hosts \
    && rm -rf ./firmware

## 启动 httpd
RUN cd ./squashfs-root \
    && cp /usr/bin/qemu-arm-static ./ \
    && mount -o bind /dev ./dev \
    && mount -t proc /proc ./proc \
    && chroot . ./qemu-arm-static ./usr/sbin/httpd &
