#!/bin/sh

wget --mirror -A zip,pkg,rar,bin,img --ignore-case ftp://ftp2.dlink.com/PRODUCTS -P output
# wget --mirror -A zip,pkg,rar,bin,img ftp://ftp.dlink.eu/Products -P output
# wget --mirror -A zip,pkg,rar,bin,img ftp://ftp.dlink.ru/pub -P output -P output
# wget --mirror -A zip,pkg,rar,bin,img ftp://ftp.d-link.co.za -P output

wget --mirror -A image --ignore-case ftp://ftp.avm.de/fritz.box -P output

wget --mirror -A img,chk,bin,stk,zip,tar,sys,rar,pkg,rmt --ignore-case ftp://downloads.netgear.com -P output

wget --mirror -A zip --ignore-case ftp://ftp.zyxel.com -P output

wget --mirror -A bin --ignore-case ftp://ftp.dd-wrt.com -P output

git clone https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git output/linux-firmware
