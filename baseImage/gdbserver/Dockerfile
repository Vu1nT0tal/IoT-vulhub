FROM firmianay/ubuntu1604
LABEL Author="firmianay@gmail.com"

WORKDIR /root

RUN apt-get update \
    && apt-get install -y xz-utils gcc make gcc-arm-linux-gnueabi gcc-mips-linux-gnu gcc-mipsel-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

COPY ./run.sh /root/run.sh

ENTRYPOINT [ "/root/run.sh" ]
