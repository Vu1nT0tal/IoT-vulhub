FROM firmianay/ubuntu1604 AS builder
LABEL Author="firmianay@gmail.com"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cmake build-essential gcc git

RUN git clone --depth=1 -b dev https://github.com/qilingframework/qiling.git \
    && cd qiling && pip3 wheel . -w wheels

FROM firmianay/ubuntu1604 AS base

COPY --from=builder /qiling /root/qiling

WORKDIR /root

RUN apt-get update \
  && apt-get install -y libmagic-dev \
  && cd ./qiling && pip3 install wheels/*.whl \
  && rm -rf wheels && rm -rf /var/lib/apt/lists/*

CMD bash
