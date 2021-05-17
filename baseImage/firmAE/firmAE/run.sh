#!/bin/bash

if [ -e ./firmae.config ]; then
    source ./firmae.config
elif [ -e ../firmae.config ]; then
    source ../firmae.config
else
    echo "Error: Could not find 'firmae.config'!"
    exit 1
fi

function get_option()
{
    OPTION=${1}
    if [ ${OPTION} = "-r" ] || [ ${OPTION} = "--run" ]; then
        echo "run"
    elif [ ${OPTION} = "-d" ] || [ ${OPTION} = "--debug" ]; then
        echo "debug"
    elif [ ${OPTION} = "-b" ] || [ ${OPTION} = "--boot" ]; then
        echo "boot"
    fi
}
OPTION=`get_option ${1}`

FILE="`ls -ld /root/firmware/* | grep -v "^d" | rev | cut -d " " -f 1 | rev`"
FILENAME=$(basename "${FILE}")
PING_RESULT=false

function run_emulation()
{
    echo "[*] ${FILE} emulation start!!!"

    # 固件解包
    timeout --preserve-status --signal SIGINT 300 \
        ./sources/extractor/extractor.py -nk $FILE images \
        2>&1 >/dev/null

    timeout --preserve-status --signal SIGINT 300 \
        ./sources/extractor/extractor.py -nf $FILE images \
        2>&1 >/dev/null

    IID=1
    WORK_DIR=`get_scratch ${IID}`
    mkdir -p ${WORK_DIR}
    chmod a+rwx "${WORK_DIR}"

    echo $FILENAME > ${WORK_DIR}/name
    sync

    if [ ! -e ./images/$IID.tar.gz ]; then
        echo "Extracting root filesystem failed!"
        return
    fi
    echo "[*] extract done!!!"

    # 获取体系结构
    ARCH=`./scripts/getArch.py ./images/$IID.tar.gz`
    echo "${ARCH}" > "${WORK_DIR}/architecture"

    if [ -e ./images/${IID}.kernel ]; then
        ./scripts/inferKernel.py ${IID}
    fi
    echo "[*] get architecture done!!!"

    if (! egrep -sqi "true" ${WORK_DIR}/web); then
        # 创建镜像并获取网络信息
        ./scripts/makeImage.sh $IID $ARCH $FILENAME 2>&1 > ${WORK_DIR}/makeImage.log
        echo "[*] makeImage done!!!"

        TIMEOUT=$TIMEOUT
        export TIMEOUT
        FIRMAE_NETWORK=${FIRMAE_NETWORK}
        export FIRMAE_NETWORK
        ./scripts/makeNetwork.py -i $IID -q -o -a ${ARCH}
        ln -s ./run.sh ${WORK_DIR}/run_debug.sh | true
        ln -s ./run.sh ${WORK_DIR}/run_analyze.sh | true
        ln -s ./run.sh ${WORK_DIR}/run_boot.sh | true
        echo "[*] infer network done!!!"
    else
        echo "[*] ${FILE} already succeed emulation!!!"
    fi

    if (egrep -sqi "true" ${WORK_DIR}/ping); then
        PING_RESULT=true
        IP=`cat ${WORK_DIR}/ip`
        echo "[+] Network reachable on ${IP}!"
    fi
    if (egrep -sqi "true" ${WORK_DIR}/web); then
        echo "[+] Web service on ${IP}"
    fi

    if [ ${OPTION} = "debug" ]; then
        # 调试模式
        if ($PING_RESULT); then
            echo "[+] Run debug!"
            IP=`cat ${WORK_DIR}/ip`
            ${WORK_DIR}/run_debug.sh &
            check_network ${IP} true

            sleep 10
            ./debug.py ${IID}

            sync
            kill $(ps aux | grep `get_qemu ${ARCH}` | awk '{print $2}') 2> /dev/null | true
            sleep 2
        else
            echo "[-] Network unreachable"
        fi
    elif [ ${OPTION} = "run" ]; then
        # 运行模式
        check_network ${IP} false &
        ${WORK_DIR}/run.sh
    elif [ ${OPTION} = "boot" ]; then
        # boot调试模式
        BOOT_KERNEL_PATH=`get_boot_kernel ${ARCH} true`
        BOOT_KERNEL=./binaries/`basename ${BOOT_KERNEL_PATH}`
        echo -e "[\033[32m+\033[0m] Connect with gdb-multiarch -q ${BOOT_KERNEL} -ex='target remote:1234'"
        ${WORK_DIR}/run_boot.sh
    fi
}

run_emulation
