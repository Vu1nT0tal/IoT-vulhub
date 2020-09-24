FROM firmianay/qiling
LABEL Author="firmianay@gmail.com"

WORKDIR /root

# 复制固件
COPY ./firmware/_*/squashfs-root /root/squashfs-root

# 复制工具
COPY ./qiling-emu/tools /root/tools

#COPY ./qiling-emu/run.sh /root/qiling/run.sh
#CMD [ "/bin/sh", "-c", "./qiling/run.sh" ]
