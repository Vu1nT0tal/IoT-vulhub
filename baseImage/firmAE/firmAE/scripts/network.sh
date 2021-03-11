#!/firmadyne/sh

BUSYBOX=/firmadyne/busybox
ACTION=`${BUSYBOX} cat /firmadyne/network_type`

if (${FIRMAE_NETWORK}); then
  ${BUSYBOX} sleep 10

  if [ ${ACTION} == "default" ]; then
    ${BUSYBOX} brctl addbr br0
    ${BUSYBOX} ifconfig br0 192.168.0.1
    ${BUSYBOX} brctl addif br0 eth0
    ${BUSYBOX} ifconfig eth0 0.0.0.0 up
  elif [ ${ACTION} != "None" ]; then
    NET_BRIDGE=`${BUSYBOX} cat /firmadyne/net_bridge`
    NET_INTERFACE=`${BUSYBOX} cat /firmadyne/net_interface`

    # netgear WNR2000 bridge command
    while (true); do
      ${BUSYBOX} sleep 5
      if (${BUSYBOX} brctl show | ${BUSYBOX} grep -sq ${NET_BRIDGE}); then
        break
      fi
    done

    ${BUSYBOX} sleep 5

    if [ ${ACTION} == "normal" ]; then
      IP=$(${BUSYBOX} ip addr show ${NET_BRIDGE} | ${BUSYBOX} grep -m1 "inet\b" | ${BUSYBOX} awk '{print $2}' | ${BUSYBOX} cut -d/ -f1)
      # tplink TL-WA860RE_EU_UK_US__V5_171116
      ${BUSYBOX} ifconfig ${NET_BRIDGE} ${IP}
      ${BUSYBOX} ifconfig ${NET_INTERFACE} 0.0.0.0 up
    elif [ ${ACTION} == "reload" ]; then
      ${BUSYBOX} ifconfig ${NET_BRIDGE} 192.168.0.1
      ${BUSYBOX} ifconfig ${NET_INTERFACE} 0.0.0.0 up
    elif [ ${ACTION} == "bridge" ]; then
      # unexpected intercept by another bridge
      # netgear WNR2000v5-V1.0.0.34
      # dlink DIR-505L_FIRMWARE_1.01.ZIP
      # tplink TL-WA850RE_V5_180228.zip
      if (${BUSYBOX} brctl show | ${BUSYBOX} grep "eth0"); then
        WAN_BRIDGE=$(${BUSYBOX} brctl show | ${BUSYBOX} grep "eth0" | ${BUSYBOX} awk '{print $1}')
        ${BUSYBOX} brctl delif ${WAN_BRIDGE} eth0
      fi
      IP=$(${BUSYBOX} ip addr show ${NET_BRIDGE} | ${BUSYBOX} grep -m1 "inet\b" | ${BUSYBOX} awk '{print $2}' | ${BUSYBOX} cut -d/ -f1)
      ${BUSYBOX} ifconfig ${NET_BRIDGE} ${IP}
      ${BUSYBOX} brctl addif ${NET_BRIDGE} eth0
      ${BUSYBOX} ifconfig ${NET_INTERFACE} 0.0.0.0 up
    elif [ ${ACTION} == "bridgereload" ]; then
      if (${BUSYBOX} brctl show | ${BUSYBOX} grep "eth0"); then
        WAN_BRIDGE=$(${BUSYBOX} brctl show | ${BUSYBOX} grep "eth0" | ${BUSYBOX} awk '{print $1}')
        ${BUSYBOX} brctl delif ${WAN_BRIDGE} eth0
      fi
      ${BUSYBOX} ifconfig ${NET_BRIDGE} 192.168.0.1
      ${BUSYBOX} brctl addif ${NET_BRIDGE} eth0
      ${BUSYBOX} ifconfig ${NET_INTERFACE} 0.0.0.0 up
    fi
  fi

  ${BUSYBOX} sleep 60

  # netgear TL-WR841HP_V2_151124
  while (true); do
    if ${BUSYBOX} which iptables; then
      iptables flush | true
      iptables -F | true
      iptables -P INPUT ACCEPT | true
    fi
    ${BUSYBOX} sleep 5
  done
fi
