FROM firmianay/qemu-user-static
LABEL Author="firmianay@gmail.com"

WORKDIR /root

# 复制固件
COPY ./firmware/_*/_31* /root/firmware
RUN cp -r ./firmware/_root*/squashfs-root ./ \
    && rm -rf ./squashfs-root/etc && cp -r ./firmware/defconf/_*/_*/etc ./squashfs-root \
    && rm -rf ./firmware \ 
    && mv /usr/bin/qemu-arm-static ./squashfs-root

COPY ./user-emu/run.sh /root/run.sh
CMD [ "/bin/sh", "-c", "./run.sh" ]
