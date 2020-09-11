FROM firmianay/qemu-system:mips
LABEL Author="firmianay@gmail.com"

WORKDIR /root

# 复制固件
COPY ./firmware/_*/squashfs-root /root/squashfs-root
RUN tar czf squashfs-root.tar.gz ./squashfs-root \
    && rm -rf ./squashfs-root

COPY ./system-emu/tools /root/tools

COPY ./system-emu/run.sh /root/run.sh
CMD [ "/bin/sh", "-c", "./run.sh" ]
