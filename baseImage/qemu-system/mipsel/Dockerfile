FROM firmianay/ubuntu:16.04
LABEL Author="firmianay@gmail.com"

WORKDIR /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends qemu-system-arm bridge-utils uml-utilities net-tools expect gdb-multiarch git python3 openssh-server \
    && sed -i "s/PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config && echo "root:root" | chpasswd \
    && git clone --depth=1 https://github.com/hugsy/gef.git \
    && cp gef/gef.py ~/.gef.py && echo "source ~/.gef.py" > ~/.gdbinit && echo "export LC_CTYPE=C.UTF-8" >> ~/.bashrc \
    && apt-get purge -y --autoremove git \
    && rm -rf /var/lib/apt/lists/* /root/gef

#RUN mkdir images && cd images \
#    && wget https://people.debian.org/~aurel32/qemu/mipsel/debian_wheezy_mipsel_standard.qcow2
#    && wget https://people.debian.org/~aurel32/qemu/mipsel/vmlinux-3.2.0-4-4kc-malta

COPY ./images /root/images
