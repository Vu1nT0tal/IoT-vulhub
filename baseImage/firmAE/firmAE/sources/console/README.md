Introduction
============

This is a small binary that spawns a console on the `/dev/firmadyne` special
character device at system startup. In conjunction with a patched filesystem
and instrumented kernel, this allows an analyst to interact with an emulated
firmware image through QEMU, since some firmware images do not spawn a terminal
on the primary serial console.

Usage
=====

First, create the special character device within the firmware image:

`mknod -m 666 /firmadyne/ttyS1 c 4 65`

Next, copy this binary into the firmware image:

`cp console /firmadyne/console`

Then, it will be automatically executed by the instrumented kernel during system
bootup after the 4th `execve()` call if both `firmadyne.execute` and
`firmadyne.syscall` kernel parameters are set to 1 (this is the default).
