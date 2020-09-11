# 贡献指南

## 前期准备

Fork 本项目，将你的项目拉取到本地，根据你想制作的靶场环境，新建一个对应的分支。

## 制作基础镜像

镜像继承关系的几个例子（命名暂时先这么定，有更好的想法请告诉我）：

```
firmianay/ubuntu:16.04 -> firmianay/qemu-system:armel -> firmianay/vivotek:remote_stack_overflow-sys
firmianay/ubuntu:16.04 -> firmianay/qemu-user-static:arm -> firmianay/vivotek:remote_stack_overflow-user

firmianay/ubuntu:16.04 -> firmianay/qemu-system:mips -> firmianay/huawei:cve-2017-17215-sys

firmianay/ubuntu:16.04 -> firmianay/qemu-system:armhf -> firmianay/netgear:psv-2020-0211-sys
```

## 制作漏洞镜像

在制作镜像时，需要尽量遵守目录结构，示例如下：

```sh
/IoT-vulhub(master*) tree Vivotek/
Vivotek/                                    # 固件厂商
└── remote_stack_overflow                   # 漏洞名称
    ├── README.md                           # 说明文档
    ├── crash.png
    ├── docker-compose-system.yml           # QEMU 系统模式配置
    ├── docker-compose-user.yml             # QEMU 用户模式配置
    ├── firmware                            # 固件目录
    │   └── CC8160-VVTK-0100d.flash.zip
    ├── system-emu                          # QEMU 系统模式目录
    │   ├── Dockerfile
    │   ├── run.sh                          # 启动脚本
    │   └── tools                           # 复现所需工具脚本或程序等
    │       ├── README.md
    │       └── poc.sh
    └── user-emu                            # QEMU 用户模式目录
        ├── Dockerfile
        └── run.sh                          # 启动脚本
```

## 编写 docker-compose.yml

目前通常有三种，也可以有其他，只要能用，形式不限：

```
docker-compose -f docker-compose-user.yml build         # QEMU 用户模式模拟
docker-compose -f docker-compose-system.yml build       # QEMU 系统模式模拟
docker-compose -f docker-compose-firmadyne.yml build    # firmadyne 模拟
...
```

## 编写 README

环境搭建完成之后，编写 README，添加漏洞说明、截图、利用文档等。

## 提交pr

最后，向 IoT-vulhub 项目提交 pull request。
