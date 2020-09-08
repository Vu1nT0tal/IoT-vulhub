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
