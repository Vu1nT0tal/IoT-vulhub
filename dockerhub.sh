#!/bin/bash

# 由于 docker hub 新政策会清理 6 个月不活跃的镜像，就用这个脚本全部拉一遍...

images=(
    # baseImage
    "firmianay/ubuntu:16.04"
    "firmianay/binwalk"
    "firmianay/gdbserver"
    "firmianay/qiling"
    "firmianay/firmadyne"

    "firmianay/qemu-user-static:arm"
    "firmianay/qemu-user-static:mips"
    "firmianay/qemu-user-static:mipsel"
    "firmianay/qemu-system:arm"
    "firmianay/qemu-system:mips"
    "firmianay/qemu-system:mipsel"

    # vivotek

    # tplink

    # netgear

    # linksys

    # huawei
)

for i in ${images[@]}; do
    echo $i
    docker pull $i
done
