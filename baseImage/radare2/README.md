# radare2

有时需要对固件做一些 patch。

<https://github.com/REMnux/docker/blob/master/radare2/Dockerfile>

```sh
$ docker pull remnux/radare2

$ docker run --rm -it --cap-drop=ALL --cap-add=SYS_PTRACE -v ~/workdir:/home/nonroot/workdir remnux/radare2
```
