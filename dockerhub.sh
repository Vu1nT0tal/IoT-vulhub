#!/bin/bash

# 由于 docker hub 新政策会清理 6 个月不活跃的镜像，就用这个脚本全部拉一遍...

images=(
    # baseImage
    "firmianay/ubuntu1604"
    "firmianay/gdbserver"
    "firmianay/qiling"
    "firmianay/binwalk"
    "firmianay/binwalk:noentry" # 作为 firmadyne 和 firmae 的基础镜像
    "firmianay/firmadyne"
    "firmianay/firmae"

    "firmianay/qemu-user-static"
    "firmianay/qemu-system:arm"
    "firmianay/qemu-system:mips"
    "firmianay/qemu-system:mipsel"

    # cisco

    # dlink

    # huawei

    # netgear

    # tenda

    # tplink

    # vivotek

)

for i in ${images[@]}; do
    echo $i
    docker pull $i
done
