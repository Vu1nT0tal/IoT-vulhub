FROM ubuntu:16.04
LABEL Author="firmianay@gmail.com"

RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends python python-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

ENV PIP_NO_CACHE_DIR=1
