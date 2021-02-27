FROM ubuntu:16.04
LABEL Author="firmianay@gmail.com"

RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends python python-pip python-setuptools python-wheel && \
    # python 2 和 3 在一条命令里安装时 pip 会出错，不知道为什么；最新的 pip 已经不支持 python2 和 python3.5
    apt-get install -y --no-install-recommends python3 python3-pip python3-setuptools python3-wheel && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "pip < 21.0" -U && pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple "pip < 21.0" -U && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    apt-get install -y --no-install-recommends iputils-ping vim-tiny net-tools nmap telnet && \
    rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1
