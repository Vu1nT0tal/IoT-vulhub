# FIRMADYNE 模拟

- [Introduction](#introduction)
- [Setup](#setup)
- [Usage](#usage)
- [FAQ](#faq)
  - [run.sh is not generated](#runsh-is-not-generated)
  - [Log ends with "Kernel panic - not syncing: No working init found"](#log-ends-with-kernel-panic---not-syncing-no-working-init-found)
  - [A process crashed, e.g. do_page_fault() #2: sending SIGSEGV for invalid read access from 00000000](#a-process-crashed-eg-do_page_fault-2-sending-sigsegv-for-invalid-read-access-from-00000000)
  - [How do I debug the emulated firmware?](#how-do-i-debug-the-emulated-firmware)

## Introduction

FIRMADYNE 包含如下组件：

* 修改过的内核 (MIPS: [v2.6](https://github.com/firmadyne/kernel-v2.6), ARM: [v4.1](https://github.com/firmadyne/kernel-v4.1),
[v3.10](https://github.com/firmadyne/kernel-v3.10))
* 用户态的 [NVRAM library](https://github.com/firmadyne/libnvram) 用于模拟 NVRAM 外设
* [extractor](https://github.com/firmadyne/extractor) 用于从固件中解压文件系统和内核
* [console](https://github.com/firmadyne/console) 用于提供调试终端
* [scraper](https://github.com/firmadyne/scraper) 用于从厂商网站下载固件

## Setup

安装依赖：

```sh
$ sudo apt-get install busybox-static fakeroot git dmsetup kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan
$ git clone --recursive https://github.com/firmadyne/firmadyne.git
```

安装 binwalk：

```sh
$ git clone https://github.com/ReFirmLabs/binwalk.git
$ cd binwalk && sudo ./deps.sh
$ sudo python ./setup.py install

# Python 2.x
$ sudo apt-get install python-lzma
$ sudo -H pip install git+https://github.com/ahupp/python-magic
$ sudo -H pip install git+https://github.com/sviehb/jefferson
$ 相比于上游的 [upstream sasquatch](https://github.com/ReFirmLabs/sasquatch)，修改过的 [sasquatch fork](https://github.com/firmadyne/sasquatch) 可以在出错时终止程序。
```

下载所有需要的组件（也可以自己[编译](#compiling-from-source)）：

```sh
$ cd ./firmadyne; ./download.sh
```

安装 QEMU：

```sh
$ sudo apt-get install qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils
```

## Usage

1. 在 `firmadyne.config` 中设置 `FIRMWARE_DIR`，指向 FIRMADYNE 根目录
2. 下载一个固件，例如：Netgear WNAP320 [v2.0.3](http://www.downloads.netgear.com/files/GDC/WNAP320/WNAP320%20Firmware%20Version%202.0.3.zip) 版本
3. 使用 extractor 获得文件系统，（`-nk` no kernel；`-np` no parallel operation；`images` 压缩包目录）
   * `./extractor/extractor.py -np -nk "WNAP320 Firmware Version 2.0.3.zip" images`
4. 确定固件的体系结构
   * `./scripts/getArch.sh ./images/1.tar.gz`
5. Load the contents of the filesystem for firmware `1` into the database, populating the `object` and `object_to_image` tables.
   * `./scripts/tar2db.py -i 1 -f ./images/1.tar.gz`
6. Create the QEMU disk image for firmware `1`.
   * `sudo ./scripts/makeImage.sh 1`
7. Infer the network configuration for firmware `1`. Kernel messages are logged to `./scratch/1/qemu.initial.serial.log`.
   * `./scripts/inferNetwork.sh 1`
8. Since the Netgear firmware disabled root access from tty0, you need to mount the QEMU disk image and do some modification. 
   * `sudo ./scripts/mount.sh 1`
   * `rm scratch/1/image/etc/securetty`
   * `sudo ./scripts/umount.sh 1`
9. Emulate firmware `1` with the inferred network configuration. This will modify the configuration of the host system by creating a TAP device and adding a route.
10. The system should be available over the network, and is ready for analysis. Kernel messages are mirrored to `./scratch/1/qemu.final.serial.log`.
   * `./analyses/snmpwalk.sh 192.168.0.100`
   * `./analyses/webAccess.py 1 192.168.0.100 log.txt`
   * `mkdir exploits; ./analyses/runExploits.py -t 192.168.0.100 -o exploits/exploit -e x` (requires Metasploit Framework)
   * `sudo nmap -O -sV 192.168.0.100`
11. The default console should be automatically connected to the terminal. You may also login with `root` and `password`. Note that `Ctrl-c` is sent to the guest; use the QEMU monitor command `Ctrl-a + x` to terminate emulation.

## FAQ
### `run.sh` is not generated
This is a common error that is encountered when the network configuration is unable to be inferred. Follow the checklist below to figure out the cause.

1. `inferNetwork.sh`: Did this script find any network interfaces (e.g. `Interfaces: [br0, 192.168.0.1]`)? If so, this is a bug; please report it. Otherwise, continue below.
2. `qemu.initial.serial.log`: Does this file end with `Unable to mount root fs on unknown-block(8,1)`? If so, the initial filesystem image was not generated correctly using `kpartx`. Try deleting the scratch directory corresponding to this firmware image, and restart at `makeImage.sh`. Otherwise, the initial emulation didn't produce any useful instrumentation. Try increasing the timeout in `inferNetwork.sh` from `60` to `120` and restarting at `inferNetwork.sh`.
3. `qemu.initial.serial.log`: Did the `init` process crash, and is this preceded by a failed NVRAM operation (e.g. `nvram_get_buf: Unable to open key <foo>`)? If so, see the FAQ entries below.

### Log ends with "Kernel panic - not syncing: No working init found"
The firmware uses an initialization process with an unusual name. You'll need to manually inspect the filesystem to identify the correct one, then modify the script to specify its full path by appending a kernel boot parameter `init=<path>` to QEMU.

### A process crashed, e.g. `do_page_fault() #2: sending SIGSEGV for invalid read access from 00000000`
It is likely that the process requested a NVRAM entry that FIRMADYNE does not have a default value for. This can be fixed by manually adding a source for NVRAM entries to `NVRAM_DEFAULTS_PATH`, an entry to `NVRAM_DEFAULTS`, or a file to `OVERRIDE_POINT` in `libnvram`. For more details, see the [documentation for libnvram](https://github.com/firmadyne/libnvram). Note that the first two options involve modifying `config.h`, which will require recompilation of `libnvram`.

### How do I debug the emulated firmware?
1. With full-system QEMU emulation, compile a statically-linked `gdbserver` for the target architecture, copy it into the filesystem, attach it to the process of interest, and connect remotely using `gdb-multiarch`. You'll need a cross-compile toolchain; either use the `crossbuild-essential-*` packages supplied by Debian/Ubuntu, build it from scratch using e.g. `buildroot`, or look for GPL sources and/or pre-compiled binaries online. If you have IDA Pro, you can use IDA's pre-compiled debug servers (located in the `dbgsrv` subdirectory of the install), though they are not GDB-compatible.
2. With full-system QEMU emulation, pass the `-s -S` parameters to QEMU and connect to the stub using `target remote localhost:1234` from `gdb-multiarch`. However, the debugger won't automatically know where kernel and userspace is in memory, so you may need to manually do `add-symbol-file` in `gdb` and break around `try_to_run_init_process()` in the kernel.
2. With user-mode QEMU emulation, `chroot` into the firmware image (optional), set `LD_LIBRARY_PATH` to contain the FIRMADYNE libnvram, and pass both the `-L` parameter with the correct path to the firmware `/lib` directory, and the binary of interest to QEMU. This is easiest to debug, because you can attach directly to the process using `gdb-multiarch`, and interact directly with the process, but the system state may not be accurate since the host kernel is being used. It is also somewhat insecure, because the emulated firmware can access the host filesystem and interact with the host kernel.
