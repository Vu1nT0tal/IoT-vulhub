# IoT-vulhub

受 [Vulhub](https://github.com/vulhub/vulhub) 项目的启发，希望做一个 IoT 版的固件漏洞复现环境。

## 安装

在 Ubuntu 20.04 下安装 docker 和 docker-compose：

```sh
# 安装 pip
$ curl -s https://bootstrap.pypa.io/get-pip.py | python3

# 安装最新版 docker
$ curl -s https://get.docker.com/ | sh

# 启动 docker 服务
$ systemctl start docker

# 安装 docker-compose
$ python3 -m pip install docker-compose
```

## 使用说明

```sh
# 下载本项目
$ wget https://github.com/firmianay/IoT-vulhub/archive/master.zip -O iot-vulhub-master.zip
$ unzip iot-vulhub-master.zip && cd iot-vulhub-master

# 构建 ubuntu1604 基础镜像
$ cd baseImage/ubuntu1604 && docker build -t firmianay/ubuntu1604 .

# 构建 binwalk 容器，方便使用
$ cd baseImage/binwalk && docker build -t firmianay/binwalk .

# 进入一个漏洞环境目录
$ cd D-Link/CVE-2019-17621

# 解包固件
$ docker run --rm -v $PWD/firmware:/root/firmware firmianay/binwalk -Mer "/root/firmware/firmware.bin"

# 初始化环境（arm/mips/mipsel）
$ ./init_env.sh xxxx

# 自动化编译环境（目前通常有四种模拟方式）
$ docker-compose -f docker-compose-user.yml build         # QEMU 用户模式模拟
$ docker-compose -f docker-compose-system.yml build       # QEMU 系统模式模拟
$ docker-compose -f docker-compose-firmadyne.yml build    # firmadyne 模拟
$ docker-compose -f docker-compose-firmae.yml build       # firmae 模拟（方便调试）

# 启动整个环境
$ docker-compose -f docker-compose-xxxx.yml up

# 每个环境目录下都有相应的说明文件，请阅读该文件，进行漏洞测试

# 测试完成后，删除整个环境
$ docker-compose -f docker-compose-xxxx.yml down -v
```

注意事项：

- 在构建 qemu-system 前务必下载对应的 qemu 镜像！
- 退出 qemu 用 `Ctrl+A`，再输入 `X`
- 容器中使用 systemctl 可能会有问题，使用 `/etc/init.d/xxxx start` 代替
- 如果要从实体机直接访问 Qemu，例如打开固件的 web 界面（实体机 -> Docker -> Qemu）：
  - 首先在启动 docker 时需要将 ssh 端口映射出来，如 `-p 1234:22`
  - 然后在本地开启端口转发，如 `ssh -D 2345 root@127.0.0.1 -p 1234`
  - 最后对浏览器设置 socks5 代理 `127.0.0.1:2345`。Burpsuite/Python脚本同理。

## 漏洞环境列表

请查看[漏洞环境列表](./vuln_list.md)。

## 贡献指南

在研究漏洞的同时，也请给我们提交一份复现环境吧！[贡献指南](./CONTRIBUTING.md)。

## 开源协议

IoT-vulhub use SATA(Star And Thank Author) [License](./LICENSE), so you have to star this project before using. 🙏

## Stargazers over time

[![Stargazers over time](https://starchart.cc/firmianay/IoT-vulhub.svg)](https://starchart.cc/firmianay/IoT-vulhub)
