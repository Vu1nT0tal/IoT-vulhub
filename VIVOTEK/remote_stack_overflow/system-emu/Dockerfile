FROM firmianay/qemu-system:armel
LABEL Author="firmianay@gmail.com"

WORKDIR /root

# 复制固件
COPY ./firmware/_*/_31* /root/firmware
RUN cp -r ./firmware/_root*/squashfs-root ./ \
    && rm -rf ./squashfs-root/etc && cp -r ./firmware/defconf/_*/_*/etc ./squashfs-root \
    && tar czf squashfs-root.tar.gz ./squashfs-root \
    && rm -rf ./firmware ./squashfs-root

COPY ./system-emu/tools /root/tools

COPY ./system-emu/run.sh /root/run.sh
CMD [ "/bin/sh", "-c", "./run.sh" ]
