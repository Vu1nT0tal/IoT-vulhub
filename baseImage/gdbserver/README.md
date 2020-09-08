# gdbserver

用于交叉编译配套的 gdb/gdbserver

下载地址：http://mirrors.kernel.org/sourceware/gdb/releases

## 构建镜像

```sh
$ docker build firmianay/gdbserver .
```

## 执行编译

输入版本号 `7.11.1` 作为参数（需要先下载 `.tar.xz` 文件到对应目录）

```sh
$ mkdir 7.11.1 && wget -P 7.11.1 http://mirrors.kernel.org/sourceware/gdb/releases/gdb-7.11.1.tar.xz

$ docker run --rm -v $PWD:/root/gdbserver firmianay/gdbserver 7.11.1
```
