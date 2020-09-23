FROM firmianay/ubuntu1604
LABEL Author="firmianay@gmail.com"
# 该镜像用于构建可调试的用户级模拟

WORKDIR /root

RUN apt-get update \
    && apt-get install -y qemu-user-static \
    && apt-get install -y --no-install-recommends gdb-multiarch git \
    && git clone --depth=1 https://github.com/hugsy/gef.git \
    && cp gef/gef.py ~/.gef.py && echo "source ~/.gef.py" > ~/.gdbinit && echo "export LC_CTYPE=C.UTF-8" >> ~/.bashrc \
    && apt-get purge -y --autoremove git \
    && rm -rf /var/lib/apt/lists/*
