FROM firmianay/ubuntu:16.04
LABEL Author="firmianay@gmail.com"

WORKDIR /root

COPY config /root
COPY buildroot-2020.02.6.tar.gz /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget make binutils build-essential gcc g++ cpio unzip rsync file bc libncurses5-dev \
    # && wget -q --tries=0 https://buildroot.org/downloads/buildroot-2020.02.6.tar.gz \
    && tar xzf buildroot-2020.02.6.tar.gz && cd buildroot-2020.02.6 && mv /root/config ./.config \
    && export PATH=/root/buildroot-2020.02.6/output/host/bin:$PATH \
    && rm -rf /var/lib/apt/lists/*

COPY run.sh /root/run.sh
CMD [ "/bin/sh", "-c", "./run.sh" ]
