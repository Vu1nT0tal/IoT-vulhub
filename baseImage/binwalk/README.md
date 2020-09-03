```
$ docker run binwalk --help
$ docker run -v $PWD/samples:/samples binwalk /samples/firmware.bin
$ docker run -v $PWD/samples:/samples binwalk -Me /samples/firmware.bin -C output/
```
