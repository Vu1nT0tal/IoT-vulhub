#!/bin/bash

# 检查参数
if [ "$#" -ge 1 ]; then
    if [ "$2" == "-v" ]; then
        VERB=true
    else
    	VERB=false
    fi
else
    echo "Please specify a firmware file as first argument"
    echo "Example: ./auto_launch.sh Router-firmware.zip"
    exit 1
fi

# 检查固件文件是否存在
if [ ! -f ${1} ]; then
    echo "Input file not found: ${1}"
    exit 1
fi
FNAME=$(basename "${1}")
FNAME="${FNAME%.*}"

# 固件解包
echo 'Extracting the firmware...'
if ${VERB} ; then
    ./extractor/extractor.py -nk "${1}" images
else
    ./extractor/extractor.py -nk "${1}" images > /dev/null 2>&1
fi

# 检查 fs 文件是否存在
if [ ! -f ./images/1.tar.gz ]; then
    echo "File ./images/1.tar.gz not found, probably an extraction problem happened"
    exit 1
fi

# 获取体系结构
echo 'Getting the architecture...'
ARCH=$(./scripts/getArch.sh ./images/1.tar.gz | cut -d ' ' -f2)

# 创建镜像并获取网络信息
echo 'Creating the image...'
if ${VERB} ; then
    ./scripts/makeImage.sh 1 ${ARCH}
    ./scripts/inferNetwork.sh 1 ${ARCH}
else
    ./scripts/makeImage.sh 1 ${ARCH} > /dev/null 2>&1
    ./scripts/inferNetwork.sh 1 ${ARCH} > /dev/null 2>&1
fi

# 启动模拟
echo 'Start running...'
./scratch/1/run.sh

# 清理中间文件
echo 'Cleaning up...'
rm images/1.tar.gz
rm -rf scratch/1
