# binwalk docker

commit 3154b0012e7dbaf2b20edd5c0a2350ec64009869

## 构建镜像

```sh
$ docker build -t firmianay/binwalk .
```

## 使用方法

```sh
$ docker run --rm firmianay/binwalk --help
$ docker run --rm -v $PWD/samples:/samples firmianay/binwalk /samples/firmware.bin
$ docker run --rm -v $PWD/samples:/samples firmianay/binwalk -Mer /samples/firmware.bin
```

## 注意

由于 firmadyne 基于该镜像，需要先将 ENTRYPOINT 注释掉，然后构建 noentry 镜像：

```sh
$ docker build -t firmianay/binwalk:noentry .
```
