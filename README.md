# IoT-vulhub

受 [Vulhub](https://github.com/vulhub/vulhub) 项目的启发，希望做一个 IoT 版的漏洞复现环境。

## Installation

在 ubuntu18.04 下安装 docker/docker-compose：

```sh
# 安装 pip
curl -s https://bootstrap.pypa.io/get-pip.py | python3

# 安装最新版 docker
curl -s https://get.docker.com/ | sh

# 启动 docker 服务
service docker start

# 安装 compose
pip install docker-compose 
```

## Usage

```sh
# 下载项目
wget https://github.com/firmianay/IoT-vulhub/archive/master.zip -O iot-vulhub-master.zip
unzip iot-vulhub-master.zip
cd iot-vulhub-master

# 进入某一个漏洞/环境的目录
cd TP-Link/CVE-2017-13772

# 自动化编译环境
docker-compose build

# 启动整个环境
docker-compose up -d

# 每个环境目录下都有相应的说明文件，请阅读该文件，进行漏洞/环境测试。
# 测试完成后，删除整个环境：
docker-compose down -v
```

## Contribution

## License

IoT-vulhub is licensed under the MIT License. See LICENSE for the full license text.
