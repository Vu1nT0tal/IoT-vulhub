#!/bin/bash

if [ $# -ne 2 ]; then
    echo $0: Usage: ./test_emulator.sh [iid] [arch]
    exit 1
fi

set -e
set -u

if [ -e ./firmae.config ]; then
    source ./firmae.config
elif [ -e ../firmae.config ]; then
    source ../firmae.config
else
    echo "Error: Could not find 'firmae.config'!"
    exit 1
fi

IID=${1}
WORK_DIR=`get_scratch ${IID}`
ARCH=${2}

echo "[*] test emulator"
${WORK_DIR}/run.sh 2>&1 >${WORK_DIR}/emulation.log &

sleep 10

echo ""

IPS=()
if (egrep -sq true ${WORK_DIR}/isDhcp); then
  IPS+=("127.0.0.1")
  echo true > ${WORK_DIR}/ping
else
  IP_NUM=`cat ${WORK_DIR}/ip_num`
  for (( IDX=0; IDX<${IP_NUM}; IDX++ ))
  do
    IPS+=(`cat ${WORK_DIR}/ip.${IDX}`)
  done
fi

echo "[*] Waiting web service... from ${IPS[@]}"
read IP PING_RESULT WEB_RESULT TIME_PING TIME_WEB < <(check_network "${IPS[@]}" false)

if (${PING_RESULT}); then
    echo true > ${WORK_DIR}/ping
    echo ${TIME_PING} > ${WORK_DIR}/time_ping
    echo ${IP} > ${WORK_DIR}/ip
fi
if (${WEB_RESULT}); then
    echo true > ${WORK_DIR}/web
    echo ${TIME_WEB} > ${WORK_DIR}/time_web
fi

kill $(ps aux | grep `get_qemu ${ARCH}` | awk '{print $2}') 2> /dev/null | true

sleep 2
