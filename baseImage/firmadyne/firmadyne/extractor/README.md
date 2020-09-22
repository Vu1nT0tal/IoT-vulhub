# extractor

使用 docker 来运行 extractor：
```
$ git clone https://github.com/firmadyne/extractor.git && cd extractor
$ ./extract.sh path/to/firmware.img path/to/output/directory
```

## Dependencies

* [fakeroot](https://fakeroot.alioth.debian.org)
* [psycopg2](http://initd.org/psycopg/)
* [binwalk](https://github.com/ReFirmLabs/binwalk)
* [python-magic](https://github.com/ahupp/python-magic)

## Binwalk

* [jefferson](https://github.com/sviehb/jefferson)
* [sasquatch](https://github.com/firmadyne/sasquatch) (optional)

## Usage

extractor 会将解包的文件临时放到 `/tmp` 目录下。由于固件可能会很大，将该目录作为 `tmpfs` 挂载到一个大的内存上可以提高性能。

为了在提取过程中保留文件系统权限不变，同时避免以 root 特权执行，需要将 extractor 的执行包装在 `fakeroot` 中来模拟特权操作。

```
$ fakeroot python3 ./extractor.py -np <infile> <outdir>
```

## Notes

This tool is beta quality. In particular, it was written before the  `binwalk` API was updated to provide an interface for accessing information about the extraction of each signature match. As a result, it walks the filesystem to identify the extracted files that correspond to a given signature match. Additionally, parallel operation has not been thoroughly tested.
