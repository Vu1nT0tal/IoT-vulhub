FROM firmianay/ubuntu1604
LABEL Author="firmianay@gmail.com"

WORKDIR /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc make cmake libtool automake autoconf libmagic g++ linux-headers git libstdc++ bash vim \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth=1 -b dev https://github.com/qilingframework/qiling.git \
    && cd qiling && pip3 install . \ 
    && rm -rf /tmp/*
