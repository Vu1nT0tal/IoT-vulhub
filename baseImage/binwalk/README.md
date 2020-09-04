# binwalk docker

## 使用方法

```
$ docker run firmianay/binwalk --help
$ docker run -v $PWD/samples:/samples firmianay/binwalk /samples/firmware.bin
$ docker run -v $PWD/samples:/samples firmianay/binwalk -Me /samples/firmware.bin -C output/
```
