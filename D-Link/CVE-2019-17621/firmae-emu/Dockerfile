FROM firmianay/firmae
LABEL Author="i@qvq.im"

WORKDIR /root

# 复制固件
COPY ./firmware /root/firmware

# 复制工具
COPY ./firmae-emu/tools /root/tools

COPY ./firmae-emu/run.sh /root/run.sh
CMD [ "/bin/sh", "-c", "/root/run.sh" ]
