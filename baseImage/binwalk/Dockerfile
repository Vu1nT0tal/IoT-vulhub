FROM firmianay/ubuntu:16.04
LABEL Author="firmianay@gmail.com"

WORKDIR /root

COPY master.zip /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends git wget unzip python \
    # && wget -q --tries=0 https://github.com/ReFirmLabs/binwalk/archive/master.zip \
    # && git clone --depth=1 https://github.com/ReFirmLabs/binwalk.git \
    && unzip -q master.zip && cd binwalk-master && ./deps.sh --yes && python ./setup.py install \
    && cd .. && rm -rf binwalk-master master.zip \
    && apt-get purge -y --autoremove git wget \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["binwalk"]
