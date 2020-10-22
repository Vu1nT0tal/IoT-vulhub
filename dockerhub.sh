#!/bin/bash

# 由于 docker hub 新政策会清理 6 个月不活跃的镜像，就用这个脚本全部拉一遍...

images=(
    # baseImage
    "firmianay/ubuntu1604"
    "firmianay/gdbserver"
    "firmianay/qiling"
    "firmianay/binwalk"
    "firmianay/binwalk:noentry" # 作为 firmadyne 的基础镜像
    "firmianay/firmadyne"

    "firmianay/qemu-user-static"
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
