# scraper

## Dependencies

* [scrapy](http://scrapy.org/)

## Usage

配置文件 `firmware/settings.py`。

以下载 dlink 固件为例：

```sh
$ scrapy crawl dlink
```

使用 [GNU Parallel](https://www.gnu.org/software/parallel/) 同时下载全部固件：

```sh
$ parallel -j 4 scrapy crawl ::: `for i in ./firmware/spiders/*.py; do basename ${i%.*}; done`
```
