FROM python:2-wheezy

WORKDIR /root

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git-core wget build-essential liblzma-dev liblzo2-dev zlib1g-dev unrar-free && \
    pip install -U pip

RUN git clone https://github.com/firmadyne/sasquatch && \
    cd sasquatch && \
    make && \
    make install && \
    cd .. && \
    rm -rf sasquatch

RUN git clone https://github.com/devttys0/binwalk.git && \
    cd binwalk && \
    ./deps.sh --yes && \
    python setup.py install && \
    pip install 'git+https://github.com/ahupp/python-magic' && \
    pip install 'git+https://github.com/sviehb/jefferson' && \
    cd .. && \
    rm -rf binwalk

RUN \
  adduser --disabled-password \
          --gecos '' \
          --home /home/extractor \
          extractor

USER extractor
WORKDIR /home/extractor

RUN git clone https://github.com/firmadyne/extractor.git
