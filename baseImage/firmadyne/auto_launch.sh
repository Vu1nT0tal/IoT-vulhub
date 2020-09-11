#!/usr/bin/env bash

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
FNAME=$(basename -- "${1}")
FNAME="${FNAME%.*}"

# check the images ID counter
re="^[0-9]+$"
ID=$(ls images/ | sort -n | tail -1 | cut -d '.' -f1)
if ! [[ ${ID} =~ ${re} ]] ; then
    ID="0"
fi
ID=$((ID + 1))

# 固件解包
echo 'Extracting the firmware...'
if ${VERB} ; then
    ./sources/extractor/extractor.py -np -nk "${1}" images
else
    ./sources/extractor/extractor.py -np -nk "${1}" images > /dev/null 2>&1
fi

# choose an appropriate ID for the extracted fs
FILE=$(ls images | grep -F "${FNAME}") && mv images/"${FILE}" images/${ID}.tar.gz

# check file existence
# 检查 fs 文件是否存在
if [ ! -f ./images/${ID}.tar.gz ]; then
    echo "File ./images/${ID}.tar.gz not found, probably an extraction problem happened"
    exit 1
fi

# 获取体系结构
echo 'Getting the architecture...'
ARCH=$(./scripts/getArch.sh ./images/${ID}.tar.gz | cut -d ' ' -f2)

# 创建镜像并获取网络信息
echo 'Creating the image...'
if ${VERB} ; then
    sudo ./scripts/makeImage.sh ${ID} ${ARCH}
    sudo ./scripts/inferNetwork.sh ${ID} ${ARCH}
else
    sudo ./scripts/makeImage.sh ${ID} ${ARCH} > /dev/null 2>&1
    sudo ./scripts/inferNetwork.sh ${ID} ${ARCH} > /dev/null 2>&1
fi

# 启动模拟
sudo ./scratch/${ID}/run.sh

# 清理中间文件
echo 'Cleaning up...'
rm images/${ID}.tar.gz
sudo rm -rf scratch/${ID}
