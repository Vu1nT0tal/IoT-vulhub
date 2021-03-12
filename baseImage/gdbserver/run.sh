#!/bin/bash

version="$1"

cp ./gdbserver/$version/gdb-$version.tar.xz ~/ && tar xJf "gdb-$1.tar.xz" && cd "gdb-$1"

# gdb-multiarch
#mkdir build_multi && cd build_multi
#../configure --enable-targets=`set -- arm-linux-gnueabi mips-linux-gnu mipsel-linux-gnu; IFS=,; echo "$*"`
#make -j $nproc && make install && cd ..

# arm gdbserver
mkdir build_arm_static && cd build_arm_static
CC="arm-linux-gnueabi-gcc" CXX="arm-linux-gnueabi-gcc" ../gdb/gdbserver/configure --target=arm-linux-gnueabi --host="arm-linux-gnueabi"
make LDFLAGS=-static -j $nproc && cp gdbserver ~/gdbserver/$version/arm-gdbserver && cd ..

# mips gdbserver
mkdir build_mips_static && cd build_mips_static
CC="mips-linux-gnu-gcc" CXX="mips-linux-gnu-gcc" ../gdb/gdbserver/configure --target=mips-linux-gnu --host="mips-linux-gnu"
make LDFLAGS=-static -j $nproc && cp gdbserver ~/gdbserver/$version/mips-gdbserver && cd ..

# mipsel gdbserver
mkdir build_mipsel_static && cd build_mipsel_static
CC="mipsel-linux-gnu-gcc" CXX="mipsel-linux-gnu-gcc" ../gdb/gdbserver/configure --target=mipsel-linux-gnu --host="mipsel-linux-gnu"
make LDFLAGS=-static -j $nproc && cp gdbserver ~/gdbserver/$version/mipsel-gdbserver && cd ..
