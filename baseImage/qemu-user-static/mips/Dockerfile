FROM firmianay/ubuntu:16.04
LABEL Author="firmianay@gmail.com"

RUN apt-get update \
    && apt-get install -y qemu-user-static \
    && cp /usr/bin/qemu-mips-static /root \
    && apt-get purge -y --autoremove qemu-user-static \
    && rm -rf /var/lib/apt/lists/*
