# Ubuntu 16.04 镜像

1. 替换 pypi 源，apt 源未做替换。可以通过在构建镜像语句中添加 `--build-arg MISE=TSINGHUA` 完成 apt 源的替换
2. 安装 python2 和 python3
3. 安装 iputils-ping vim-tiny net-tools nmap telnet
