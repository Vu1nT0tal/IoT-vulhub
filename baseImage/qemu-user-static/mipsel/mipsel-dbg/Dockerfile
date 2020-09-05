FROM firmianay/qemu-user-static:mipsel
LABEL Author="firmianay@gmail.com"

WORKDIR /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends gdb-multiarch git python3 \
    && git clone --depth=1 https://github.com/hugsy/gef.git \
    && cp gef/gef.py ~/.gef.py && echo "source ~/.gef.py" > ~/.gdbinit && echo "export LC_CTYPE=C.UTF-8" >> ~/.bashrc \
    && apt-get purge -y --autoremove git \
    && rm -rf gef /var/lib/apt/lists/* 
