# binwalk docker

## 构建镜像

```sh
$ docker build -t firmianay/binwalk .
```

## 使用方法

```sh
$ docker run firmianay/binwalk --help
$ docker --rm run -v $PWD/samples:/samples firmianay/binwalk /samples/firmware.bin
$ docker --rm run -v $PWD/samples:/samples firmianay/binwalk -Me /samples/firmware.bin -C output/
```

## 注意

由于 firmadyne 基于该镜像，需要先将 ENTRYPOINT 注释掉，然后构建 noentry 镜像：

```sh
$ docker build -t firmianay/binwalk:noentry .
```
