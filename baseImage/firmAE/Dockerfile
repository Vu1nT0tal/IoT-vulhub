FROM firmianay/binwalk:noentry

WORKDIR /root

COPY ./firmAE ./firmAE

RUN apt update && \
    apt install -y sudo busybox-static bash-static fakeroot dmsetup kpartx netcat nmap snmp uml-utilities util-linux vlan bc && \
    apt install -y qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils && \
    apt-get install -y --no-install-recommends curl openssh-server && \
    sed -i "s/PermitRootLogin prohibit-password/PermitRootLogin yes/g" /etc/ssh/sshd_config && echo "root:root" | chpasswd && echo "GatewayPorts yes" >>  /etc/ssh/sshd_config && \
    pip3 install python-magic && rm -rf /var/lib/apt/lists/*