# FirmAE 模拟

<https://github.com/pr0v3rbs/FirmAE>

注：添加 `get_device_firmadyne` 函数替换 `add_partition`，修复 loop device 错误。

## 构建镜像

使用方法与 firmadyne 相同，需要先构建 `binwalk:noentry` 镜像（查看 binwalk 目录）。

```sh
$ docker build -t firmianay/firmae .
```

## 使用方法

启动固件模拟：

```sh
$ sudo ./run.sh --run
```

启动固件模拟并用户层调试：

```sh
$ sudo ./run.sh --debug
```

启动固件模拟并内核层 boot 调试：

```sh
$ sudo ./run.sh --boot
```
