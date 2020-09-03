FROM ubuntu:16.04
LABEL Author="firmianay@gmail.com"

WORKDIR /root

COPY master.zip /root

RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends python python-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN apt-get update \
    && apt-get install -y --no-install-recommends git wget unzip python \
    # && wget -q --tries=0 https://github.com/ReFirmLabs/binwalk/archive/master.zip \
    # && git clone --depth=1 https://github.com/ReFirmLabs/binwalk.git \
    && unzip -q master.zip && cd binwalk-master && ./deps.sh --yes && python ./setup.py install \
    && cd .. && rm -rf binwalk-master master.zip \
    && apt-get purge -y --autoremove git wget unzip \
    && rm -rf /var/lib/apt/lists/*

RUN  binwalk -h > /dev/null

ENTRYPOINT ["/usr/bin/binwalk"]
