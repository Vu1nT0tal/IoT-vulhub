FROM firmianay/firmadyne
LABEL Author="firmianay@gmail.com"

WORKDIR /root

# 复制固件
COPY ./firmware /root/firmware

# 复制工具
COPY ./firmadyne-emu/tools /root/tools

COPY ./firmadyne-emu/run.sh /root/firmadyne/run.sh
CMD [ "/bin/sh", "-c", "./firmadyne/run.sh" ]
