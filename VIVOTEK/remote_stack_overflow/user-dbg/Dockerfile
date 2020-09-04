FROM firmianay/qemu-user-static:arm-dbg
LABEL Author="firmianay@gmail.com"

WORKDIR /root

# 复制固件
COPY ./firmware/_*/_*/_31* /root/firmware
RUN cp -r ./firmware/_root*/squashfs-root ./ \
    && rm -rf ./squashfs-root/etc && cp -r ./firmware/defconf/_*/_*/etc ./squashfs-root \
    && rm -rf ./firmware \ 
    && mv /root/qemu-arm-static ./squashfs-root

COPY ./run.sh /root/run.sh
CMD [ "/bin/sh", "-c", "./run.sh" ]
