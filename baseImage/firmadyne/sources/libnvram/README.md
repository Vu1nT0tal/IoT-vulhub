Introduction
============

This is a library that emulates the behavior of the NVRAM peripheral, by
storing key-value pairs into a `tmpfs` mounted at `MOUNT_POINT` (default:
`/firmadyne/libnvram`).

Upon first access of a NVRAM-related function, the emulated peripheral is
initialized as follows:

1. The NVRAM filesystem is mounted
2. Built-in default values are loaded from the `NVRAM_DEFAULTS` macro
3. A built-in list of system-specific default value sources, defined by
   the `NVRAM_DEFAULTS_PATH` macro, is iteratively checked and loaded. This
   includes native functions (`NATIVE()` macro), text files on the filesystem
   (`PATH()` macro), and loaded symbols of type `char *[]` (`TABLE()` macro).
4. System-specific override values are loaded from keys located at
   `OVERRIDE_POINT` (default: `/firmadyne/libnvram.override`)

Due to differences in C runtime libraries on various firmware, this library
is compiled as a dynamically-linked shared library. Since ELF dynamic loaders
on Linux systems support lazy linking and global symbol resolution scope,
resolution of external symbols used by this library are effectively delayed
until after the calling process has already loaded the system C runtime library.
As a result, this library behaves like a statically-linked shared library, while
dynamically using functions loaded by the calling process, including
those from the standard C runtime library.

Although compilation as a statically-linked shared library might appear to
preferable, in practice we've had better results using our approach discussed
above. Different C runtime libraries may have incompatible implementations of
features such as thread-local storage. Additionally, many C runtime libraries
are not built with position-independent code (PIC) to support static
compilation.

Usage
=====

Build the library, and copy it into the firmware image:

`cp libnvram.so /firmadyne/libnvram.so`

Create the NVRAM storage directories on the filesystem:

`mkdir -p /firmadyne/libnvram/`
`mkdir -p /firmadyne/libnvram.override/`

This will be automatically loaded by the instrumented kernel through
`LD_PRELOAD` by modifications to `init/main.c`.

Notes
=====

This library is alpha quality. In particular, memory safety of string
operations has not been checked, there may be concurrency bugs, and it uses
some nasty hacks. Additionally, various firmware have different calling
semantics for NVRAM-related functions, which may not be supported by this
library, or may be mutually incompatible with other devices.

Furthermore, this library is missing graceful fallbacks for library
functions not available in certain C runtime libraries. This is because C
runtime libraries only maintain source-level compatibility with one another,
not binary-level compatibility. As a result, fallbacks need to be manually
implemented by declaring library functions to be weak symbols and checking for
initialization before calling them. Currently, uses of `ftok()` are implemented
in this manner, meaning that semaphores are not used if this function is
unavailable. This is not desirable, but preferred over a NULL pointer
dereference.

As another example, `stat()` is not necessarily available at the binary level
in all C runtime libraries. [GNU glibc](https://www.gnu.org/software/libc/)
only exports `stat()` as a private weak symbol, linking instead to `__xstat()`,
which is part of the
[Linux Standard Base (LSB)](http://refspecs.linuxfoundation.org/lsb.shtml)
specification. However, [uClibc](https://uclibc.org/) instead links to
`__xstat_conv()`, and does not provide a `__xstat()` function. Furthermore,
most libraries will prefer `stat64()` over `stat()`, depending on whether
Large File Support (LFS) is enabled, which results in additional indirection.
Additionally, making a direct syscall to `sys_stat()` can be unpredictable due
to changes in the system call interface. As an alternative, use `access()` or
`fopen()`.

Unfortunately, any of these failures typically cause the `init` process to crash
during system startup, potentially with a NULL pointer dereference. This is
because some firmware assume that NVRAM-related functions will never
return NULL, making it difficult to debug. Resolving this typically requires
manual reverse engineering to identify the crashing function, and modifying
the NVRAM library by defining a default value, adding a source of default
values, or writing a shim function to call into this library to perform a
NVRAM-related operation.

Pull requests are greatly appreciated!
