FROM ubuntu:20.04

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

USER root
RUN apt-get update && apt-get install -y sudo ccache wget build-essential git && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r nonroot && \
    useradd -m -d /home/nonroot -g nonroot -s /usr/sbin/nologin -c "Nonroot User" nonroot && \
    mkdir -p /home/nonroot/workdir && \
    chown -R nonroot:nonroot /home/nonroot && \
    usermod -a -G sudo nonroot && echo 'nonroot:nonroot' | chpasswd && \
			  echo "nonroot ALL=(ALL) NOPASSWD: ALL" >/etc/sudoers.d/nonroot && \
    mkdir /usr/local/radare2 && \
    chown nonroot:nonroot /usr/local/radare2
  
USER nonroot
RUN git clone -b master --depth 1  https://github.com/radare/radare2.git /usr/local/radare2 && \
    cd /usr/local/radare2 && \
    ./sys/install.sh && \
    r2pm init && \
    r2pm update

USER root
RUN chown -R root:root /usr/local/radare2

USER nonroot
ENV HOME /home/nonroot
WORKDIR /home/nonroot/workdir
VOLUME ["/home/nonroot/workdir"]
EXPOSE 8080
CMD ["/bin/bash"]
