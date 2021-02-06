FROM firmianay/ubuntu1604
LABEL Author="firmianay@gmail.com"

ARG ARCH

WORKDIR /root

COPY config /root/config
COPY buildroot-2020.02.6.tar.gz /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget make binutils build-essential gcc g++ cpio unzip rsync file bc libncurses5-dev \
    && tar xzf buildroot-2020.02.6.tar.gz \
    && export PATH=/root/buildroot-2020.02.6/output/host/bin:$PATH \
    && rm buildroot-2020.02.6.tar.gz \
    && rm -rf /var/lib/apt/lists/*

COPY run.sh /root/run.sh
CMD [ "/bin/sh", "-c", "./run.sh ${ARCH}"]
