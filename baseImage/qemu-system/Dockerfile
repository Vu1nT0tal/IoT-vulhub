FROM firmianay/ubuntu:16.04
LABEL Author="firmianay@gmail.com"

RUN apt-get update \
    && apt-get install -y --no-install-recommends qemu-system \
    && rm -rf /var/lib/apt/lists/*
