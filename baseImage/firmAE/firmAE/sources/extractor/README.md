# extractor

## Dependencies

* [binwalk](https://github.com/ReFirmLabs/binwalk)
* [python-magic](https://github.com/ahupp/python-magic)

## Binwalk

* [jefferson](https://github.com/sviehb/jefferson)
* [sasquatch](https://github.com/firmadyne/sasquatch) (optional)

## Usage

extractor 会将解包的文件临时放到 `/tmp` 目录下。由于固件可能会很大，将该目录作为 `tmpfs` 挂载到一个大的内存上可以提高性能。

```sh
$ python3 ./extractor.py <infile> <outdir>
```
