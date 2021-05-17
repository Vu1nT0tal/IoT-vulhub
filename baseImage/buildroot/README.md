# buildroot

## 手动编译工具链

1. 从 `https://buildroot.org/` 下载 Buildroot
2. 执行命令 `make menuconfig`
3. 在 `Target options` 中选择硬件平台和 ABI，在 `Toolchain` 中选择本机的内核版本（`uname -r`），然后保存退出
4. 执行命令 `make toolchain`
5. 完成后查看目录 `output/host/bin/`

```sh
# 参数 ARCH 可以取 arm/mips/mipsel
$ docker build --build-arg ARCH=arm -t firmianay/buildroot .
$ docker run --rm -it firmianay/buildroot /bin/bash
# 进入容器
$ cd buildroot-2020.02.6 && make toolchain
```

```sh
# 交叉编译示例
$ sudo docker cp system-emu/nvram.c e95f9d0fdd1d:/root
# 进入容器
$ arm-buildroot-linux-uclibcgnueabi-gcc -Wall -fPIC -shared nvram.c -o nvram.so
```

## 或者下载直接使用

<https://toolchains.bootlin.com>

```sh
# armv5-eabi uclibc
$ wget https://toolchains.bootlin.com/downloads/releases/toolchains/armv5-eabi/tarballs/armv5-eabi--uclibc--stable-2020.08-1.tar.bz2

# mips32 uclibc
$ wget https://toolchains.bootlin.com/downloads/releases/toolchains/mips32/tarballs/mips32--uclibc--stable-2020.08-1.tar.bz2

# mips32el uclibc
$ wget https://toolchains.bootlin.com/downloads/releases/toolchains/mips32el/tarballs/mips32el--uclibc--stable-2020.08-1.tar.bz2
```

或者：<https://www.uclibc.org/downloads/binaries/0.9.30.1>
