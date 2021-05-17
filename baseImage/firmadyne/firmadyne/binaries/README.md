# firmadyne 所需文件

- console
  - `console.armel`
  - `console.mipseb`
  - `console.mipsel`
- libnvram
  - `libnvram.so.armel`
  - `libnvram.so.mipseb`
  - `libnvram.so.mipsel`
- kernel
  - `zImage.armel`
  - `vmlinux.mipseb`
  - `vmlinux.mipsel`

```sh
#!/bin/sh

set -e

echo "Downloading binaries..."

echo "Downloading kernel 2.6 (MIPS)..."
wget -O ./binaries/vmlinux.mipsel https://github.com/firmadyne/kernel-v2.6/releases/download/v1.1/vmlinux.mipsel
wget -O ./binaries/vmlinux.mipseb https://github.com/firmadyne/kernel-v2.6/releases/download/v1.1/vmlinux.mipseb

echo "Downloading kernel 4.1 (ARM)..."
wget -O ./binaries/zImage.armel https://github.com/firmadyne/kernel-v4.1/releases/download/v1.1/zImage.armel

echo "Downloading console..."
wget -O ./binaries/console.armel https://github.com/firmadyne/console/releases/download/v1.0/console.armel
wget -O ./binaries/console.mipseb https://github.com/firmadyne/console/releases/download/v1.0/console.mipseb
wget -O ./binaries/console.mipsel https://github.com/firmadyne/console/releases/download/v1.0/console.mipsel

echo "Downloading libnvram..."
wget -O ./binaries/libnvram.so.armel https://github.com/firmadyne/libnvram/releases/download/v1.0b/libnvram.so.armel
wget -O ./binaries/libnvram.so.mipseb https://github.com/firmadyne/libnvram/releases/download/v1.0b/libnvram.so.mipseb
wget -O ./binaries/libnvram.so.mipsel https://github.com/firmadyne/libnvram/releases/download/v1.0b/libnvram.so.mipsel

echo "Done!"
```
