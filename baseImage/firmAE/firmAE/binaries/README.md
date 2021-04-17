# firmAE 所需文件

```sh
#!/bin/sh

set -e

download(){
    wget -N --continue -P./binaries/ $*
}

echo "Downloading binaries..."

echo "Downloading kernel 2.6 (MIPS)..."
download https://github.com/pr0v3rbs/FirmAE_kernel-v2.6/releases/download/v1.0/vmlinux.mipsel.2
download https://github.com/pr0v3rbs/FirmAE_kernel-v2.6/releases/download/v1.0/vmlinux.mipseb.2

echo "Downloading kernel 4.1 (MIPS)..."
download https://github.com/pr0v3rbs/FirmAE_kernel-v4.1/releases/download/v1.0/vmlinux.mipsel.4
download https://github.com/pr0v3rbs/FirmAE_kernel-v4.1/releases/download/v1.0/vmlinux.mipseb.4

echo "Downloading kernel 4.1 (ARM)..."
download https://github.com/pr0v3rbs/FirmAE_kernel-v4.1/releases/download/v1.0/zImage.armel
download https://github.com/pr0v3rbs/FirmAE_kernel-v4.1/releases/download/v1.0/vmlinux.armel

echo "Downloading busybox..."
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/busybox.armel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/busybox.mipseb
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/busybox.mipsel

echo "Downloading console..."
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/console.armel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/console.mipseb
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/console.mipsel

echo "Downloading libnvram..."
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/libnvram.so.armel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/libnvram.so.mipseb
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/libnvram.so.mipsel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/libnvram_ioctl.so.armel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/libnvram_ioctl.so.mipseb
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/libnvram_ioctl.so.mipsel

echo "Downloading gdb..."
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/gdb.armel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/gdb.mipseb
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/gdb.mipsel

echo "Downloading gdbserver..."
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/gdbserver.armel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/gdbserver.mipseb
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/gdbserver.mipsel

echo "Downloading strace..."
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/strace.armel
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/strace.mipseb
download https://github.com/pr0v3rbs/FirmAE/releases/download/v1.0/strace.mipsel

echo "Done!"
```
