# Ubuntu 16.04 镜像

1. 考虑到稳定性，未对 apt 源和 pypi 源进行替换。可以通过在构建镜像语句中添加 `--build-arg MISE=TSINGHUA` 完成替换
2. 安装 python2 和 python3
3. 安装 iputils-ping vim-tiny net-tools nmap telnet
