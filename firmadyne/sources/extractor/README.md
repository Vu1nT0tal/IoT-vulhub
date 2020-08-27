Introduction
============

This is a recursive firmware extractor that aims to extract a kernel image 
and/or compressed filesystem from a Linux-based firmware image. A number of 
heuristics are included to avoid extraction of certain blacklisted file types, 
and to avoid unproductive extraction beyond certain breadth and depth 
limitations.

Firmware images with multiple filesystems are not fully supported; this tool
cannot reassemble them and will instead extract the first filesystem that has
sufficient UNIX-like root directories (e.g. `/bin`, `/etc/`, etc.)

For the impatients: Dockerize all the things!
=============================================
1. Install [Docker](https://docs.docker.com/engine/getstarted/)
2. Run the dockerized extractor
```
git clone https://github.com/firmadyne/extractor.git
cd extractor
./extract.sh path/to/firmware.img path/to/output/directory
```

Dependencies
============
* [fakeroot](https://fakeroot.alioth.debian.org)
* [psycopg2](http://initd.org/psycopg/)
* [binwalk](https://github.com/devttys0/binwalk)
* [python-magic](https://github.com/ahupp/python-magic)

Please use the latest version of `binwalk`. Note that there are two
Python modules that both share the name `python-magic`; both should be usable,
but only the one linked above has been tested extensively.

Binwalk
-------

* [jefferson](https://github.com/sviehb/jefferson)
* [sasquatch](https://github.com/firmadyne/sasquatch) (optional)

When installing `binwalk`, it is optional to use the forked version of the
`sasquatch` tool, which has been modified to make SquashFS file extraction
errors fatal to prevent false positives.

Usage
=====

During execution, the extractor will temporarily extract files into `/tmp`
while recursing. Since firmware images can be large, preferably mount this
mount point as `tmpfs` backed by a large amount of memory, to optimize
performance.

To preserve filesystem permissions during extraction, while avoiding execution
with root privileges, wrap execution of this extractor within `fakeroot`. This
will emulate privileged operations.

`fakeroot python3 ./extractor.py -np <infile> <outdir>`

Notes
=====

This tool is beta quality. In particular, it was written before the 
`binwalk` API was updated to provide an interface for accessing information
about the extraction of each signature match. As a result, it walks the
filesystem to identify the extracted files that correspond to a given
signature match. Additionally, parallel operation has not been thoroughly
tested.

Pull requests are greatly appreciated!
