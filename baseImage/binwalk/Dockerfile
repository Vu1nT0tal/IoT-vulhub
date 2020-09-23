FROM firmianay/ubuntu1604
LABEL Author="firmianay@gmail.com"

WORKDIR /root

COPY binwalk-master.zip /root

RUN apt-get update \
    && apt-get install -y --no-install-recommends git wget unzip python3-dev \
    # && git clone --depth=1 https://github.com/ReFirmLabs/binwalk.git \
    && unzip -q binwalk-master.zip && cd binwalk-master \
    # https://github.com/devttys0/sasquatch/pull/35
    && sed -i 's/devttys0\/sasquatch/firmianay\/sasquatch -b patch-1/g' deps.sh \
    && ./deps.sh --yes && python3 ./setup.py install \
    && cd .. && rm -rf binwalk-master binwalk-master.zip \
    && apt-get purge -y --autoremove git wget \
    && rm -rf /var/lib/apt/lists/*

# comment it for 'noentry'
ENTRYPOINT ["binwalk"]
