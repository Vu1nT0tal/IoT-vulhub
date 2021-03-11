#!/bin/bash

if [ -e ./firmadyne.config ]; then
    source ./firmadyne.config
elif [ -e ../firmadyne.config ]; then
    source ../firmadyne.config
else
    echo "Error: Could not find 'firmadyne.config'!"
    exit 1
fi

if check_number $1; then
    echo "Usage: $0 <image ID>"
    echo "This script deletes a whole project"
    exit 1
fi
IID=${1}

# 检查是否有 QEMU 在运行
echo "checking the process table for a running qemu instance ..."
PID=`ps -ef | grep qemu | grep "${IID}" | grep -v grep | awk '{print $2}'`
if ! [ -z $PID ]; then
    echo "killing process ${PID}"
    kill -9 ${PID}
fi

PID1=`ps -ef | grep "${IID}\/run.sh" | grep -v grep | awk '{print $2}'`
if ! [ -z $PID1 ]; then
    echo "killing process ${PID1}"
    kill ${PID1}
fi

# 检查文件系统是否已挂载
echo "In case the filesystem is mounted, umount it now ..."
./scripts/umount.sh ${IID}

# 检查网络配置
echo "In case the network is configured, reconfigure it now ..."
for i in 0 .. 4; do
    ifconfig tap${IID}_${i} down
    tunctl -d tap${IID}_${i}
done

# 清理文件系统
echo "Clean up the file system ..."
if [ -f "/tmp/qemu.${IID}*" ]; then
    rm /tmp/qemu.${IID}*
fi

if [ -f ./images/${IID}.tar.gz ]; then
    rm ./images/${IID}.tar.gz
fi

if [ -f ./images/${IID}.kernel ]; then
    rm ./images/${IID}.kernel
fi

if [ -d ./scratch/${IID}/ ]; then
    rm -r ./scratch/${IID}/
fi

echo "Done. Removed project ID ${IID}."
