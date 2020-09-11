# buildroot

## 手动编译工具链

1. 从 `https://buildroot.org/` 下载 Buildroot
2. 执行命令 `make menuconfig`
3. 在 `Target options` 中选择硬件平台和 ABI，在 `Toolchain configure` 中选择所需工具链，然后保存退出
4. 执行命令 `make toolchain`
5. 完成后查看目录 `output/host/bin/`

```sh
$ docker build firmianay/buildroot .
$ docker run --rm -it firmianay/buildroot /bin/bash
```

## 或者下载直接使用

https://toolchains.bootlin.com/

```sh
# armv5-eabi uclibc
$ wget https://toolchains.bootlin.com/downloads/releases/toolchains/armv5-eabi/tarballs/armv5-eabi--uclibc--stable-2020.02-2.tar.bz2

# mips32 uclibc
$ wget https://toolchains.bootlin.com/downloads/releases/toolchains/mips32/tarballs/mips32--uclibc--stable-2020.02-2.tar.bz2

# mips32el uclibc
$ wget https://toolchains.bootlin.com/downloads/releases/toolchains/mips32el/tarballs/mips32el--uclibc--stable-2020.02-2.tar.bz2
```
