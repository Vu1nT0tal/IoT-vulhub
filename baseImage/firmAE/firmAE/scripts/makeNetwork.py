#!/usr/bin/env python3

import sys
import getopt
import re
import struct
import socket
import stat
import os
import time
import subprocess

debug = 0
SCRATCHDIR = ''
SCRIPTDIR = ''

QEMUCMDTEMPLATE = """#!/bin/bash

set -e
set -u

ARCHEND=%(ARCHEND)s
IID=%(IID)i

if [ -e ./firmae.config ]; then
    source ./firmae.config
elif [ -e ../firmae.config ]; then
    source ../firmae.config
elif [ -e ../../firmae.config ]; then
    source ../../firmae.config
else
    echo "Error: Could not find 'firmae.config'!"
    exit 1
fi

RUN_MODE=`basename ${0}`

IMAGE=`get_fs ${IID}`
if (echo ${ARCHEND} | grep -q "mips" && echo ${RUN_MODE} | grep -q "debug"); then
    KERNEL=`get_kernel ${ARCHEND} true`
else
    KERNEL=`get_kernel ${ARCHEND} false`
fi

if (echo ${RUN_MODE} | grep -q "analyze"); then
    QEMU_DEBUG="user_debug=31 firmadyne.syscall=32"
else
    QEMU_DEBUG="user_debug=0 firmadyne.syscall=1"
fi

if (echo ${RUN_MODE} | grep -q "boot"); then
    QEMU_BOOT="-s -S"
else
    QEMU_BOOT=""
fi

QEMU=`get_qemu ${ARCHEND}`
QEMU_MACHINE=`get_qemu_machine ${ARCHEND}`
QEMU_ROOTFS=`get_qemu_disk ${ARCHEND}`
WORK_DIR=`get_scratch ${IID}`

# DEVICE=`add_partition "${WORK_DIR}/image.raw"`
DEVICE=$(get_device_firmadyne "$(kpartx -a -s -v "${WORK_DIR}/image.raw")")
mount ${DEVICE} ${WORK_DIR}/image > /dev/null

echo "%(NETWORK_TYPE)s" > ${WORK_DIR}/image/firmadyne/network_type
echo "%(NET_BRIDGE)s" > ${WORK_DIR}/image/firmadyne/net_bridge
echo "%(NET_INTERFACE)s" > ${WORK_DIR}/image/firmadyne/net_interface

echo "#!/firmadyne/sh" > ${WORK_DIR}/image/firmadyne/debug.sh
if (echo ${RUN_MODE} | grep -q "debug"); then
    echo "while (true); do /firmadyne/busybox nc -lp 31337 -e /firmadyne/sh; done &" >> ${WORK_DIR}/image/firmadyne/debug.sh
    echo "/firmadyne/busybox telnetd -p 31338 -l /firmadyne/sh" >> ${WORK_DIR}/image/firmadyne/debug.sh
fi
chmod a+x ${WORK_DIR}/image/firmadyne/debug.sh

sleep 1
sync
umount ${WORK_DIR}/image > /dev/null
del_partition ${DEVICE:0:$((${#DEVICE}-2))}

%(START_NET)s

echo "Starting firmware emulation..."

%(QEMU_ENV_VARS)s ${QEMU} ${QEMU_BOOT} -m 1024 -M ${QEMU_MACHINE} -kernel ${KERNEL} \\
    %(QEMU_DISK)s -append "root=${QEMU_ROOTFS} console=ttyS0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 %(QEMU_INIT)s rw debug ignore_loglevel print-fatal-signals=1 FIRMAE_NETWORK=${FIRMAE_NETWORK} FIRMAE_NVRAM=${FIRMAE_NVRAM} FIRMAE_KERNEL=${FIRMAE_KERNEL} FIRMAE_ETC=${FIRMAE_ETC} ${QEMU_DEBUG}" \\
    -serial file:${WORK_DIR}/qemu.final.serial.log \\
    -serial unix:/tmp/qemu.${IID}.S1,server,nowait \\
    -monitor unix:/tmp/qemu.${IID},server,nowait \\
    -display none \\
    %(QEMU_NETWORK)s | true

%(STOP_NET)s

echo "Done!"
"""

def mountImage(targetDir):
    # loopFile = subprocess.check_output(['bash', '-c', 'source firmae.config && add_partition %s/image.raw' % targetDir]).decode().strip()
    loopFile = subprocess.check_output(['bash', '-c', 'source firmae.config && get_device_firmadyne "$(kpartx -a -s -v "%s/image.raw")"' % targetDir]).decode().strip()
    os.system('mount %s %s/image > /dev/null' % (loopFile, targetDir))
    time.sleep(1)
    return loopFile

def umountImage(targetDir, loopFile):
    os.system('umount %s/image > /dev/null' % targetDir)
    subprocess.check_output(['bash', '-c', 'source firmae.config && del_partition %s' % loopFile.rsplit('p', 1)[0]])

def checkVariable(key):
    if os.environ[key] == 'true':
        return True
    else:
        return False

def stripTimestamps(data):
    lines = data.split(b"\n")
    prog = re.compile(b"^\[[^\]]*\] firmadyne: ")
    lines = [prog.sub(b"", l) for l in lines]
    return lines

def findMacChanges(data, endianness):
    lines = stripTimestamps(data)
    candidates = filter(lambda l: l.startswith(b"ioctl_SIOCSIFHWADDR"), lines)
    if debug:
        print("Mac Changes %r" % candidates)

    result = []
    if endianness == "eb":
        fmt = ">I"
    elif endianness == "el":
        fmt = "<I"
    prog = re.compile(b"^ioctl_SIOCSIFHWADDR\[[^\]]+\]: dev:([^ ]+) mac:0x([0-9a-f]+) 0x([0-9a-f]+)")
    for c in candidates:
        g = prog.match(c)
        if g:
            (iface, mac0, mac1) = g.groups()
            iface = iface.decode('utf-8')
            m0 = struct.pack(fmt, int(mac0, 16))[2:]
            m1 = struct.pack(fmt, int(mac1, 16))
            mac = "%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", m0+m1)
            result.append((iface, mac))
    return result

def findPorts(data, endianness):
    lines = stripTimestamps(data)
    candidates = filter(lambda l: l.startswith(b"inet_bind"), lines) # logs for the inconfig process
    result = []
    if endianness == "eb":
        fmt = ">I"
    elif endianness == "el":
        fmt = "<I"
    prog = re.compile(b"^inet_bind\[[^\]]+\]: proto:SOCK_(DGRAM|STREAM), ip:port: 0x([0-9a-f]+):([0-9]+)")
    portSet = {}
    for c in candidates:
        g = prog.match(c)
        if g:
            (proto, addr, port) = g.groups()
            proto = "tcp" if proto == b"STREAM" else "udp"
            addr = socket.inet_ntoa(struct.pack(fmt, int(addr, 16)))
            port = int(port.decode())
            if port not in portSet:
                result.append((proto, addr, port))
                portSet[port] = True
    return result

# Get the netwokr interfaces in the router, except 127.0.0.1
def findNonLoInterfaces(data, endianness):
    lines = stripTimestamps(data)
    candidates = filter(lambda l: l.startswith(b"__inet_insert_ifa"), lines) # logs for the inconfig process
    if debug:
        print("Candidate ifaces: %r" % candidates)
    result = []
    if endianness == "eb":
        fmt = ">I"
    elif endianness == "el":
        fmt = "<I"
    prog = re.compile(b"^__inet_insert_ifa\[[^\]]+\]: device:([^ ]+) ifa:0x([0-9a-f]+)")
    for c in candidates:
        g = prog.match(c)
        if g:
            (iface, addr) = g.groups()
            iface = iface.decode('utf-8')
            addr = socket.inet_ntoa(struct.pack(fmt, int(addr, 16)))
            if addr != "127.0.0.1" and addr != "0.0.0.0":
                result.append((iface, addr))
    return result

def findIfacesForBridge(data, brif):
    lines = stripTimestamps(data)
    result = []
    candidates = filter(lambda l: l.startswith(b"br_dev_ioctl") or l.startswith(b"br_add_if"), lines)
    progs = [re.compile(p % brif.encode()) for p in [b"^br_dev_ioctl\[[^\]]+\]: br:%s dev:(.*)", b"^br_add_if\[[^\]]+\]: br:%s dev:(.*)"]]
    for c in candidates:
        for p in progs:
            g = p.match(c)
            if g:
                iface = g.group(1)
                iface = iface.decode('utf-8')
                #we only add it if the interface is not the bridge itself
                #there are images that call brctl addif br0 br0 (e.g., 5152)
                if iface != brif:
                    result.append(iface.strip())
    return result

def findVlanInfoForDev(data, dev):
    lines = stripTimestamps(data)
    results = []
    candidates = filter(lambda l: l.startswith(b"register_vlan_dev"), lines)
    prog = re.compile(b"register_vlan_dev\[[^\]]+\]: dev:%s vlan_id:([0-9]+)" % dev.encode())
    for c in candidates:
        g = prog.match(c)
        if g:
            results.append(int(g.group(1)))
    return results

def ifaceNo(dev):
    g = re.match(r"[^0-9]+([0-9]+)", dev)
    return int(g.group(1)) if g else -1

def isDhcpIp(ip):
    # normal dhcp client ip
    if ip.startswith("10.0.2."):
        return True
    # netgear armel R6900 series
    elif ip.endswith(".190"):
        return True
    return False

def qemuArchNetworkConfig(i, tap_num, arch, n, isUserNetwork, ports):
    if arch == "arm":
        device = "virtio-net-device"
    else:
        device = "e1000"

    if not n:
        return "-device %(DEVICE)s,netdev=net%(I)i -netdev socket,id=net%(I)i,listen=:200%(I)i" % {'DEVICE': device, 'I': i}
    else:
        (ip, dev, vlan, mac, brif) = n
        vlan_id = vlan if vlan else i
        mac_str = "" if not mac else ",macaddr=%s" % mac
        if isUserNetwork: # user network dhcp server
            # TODO: get port list (inet_bind)
            # TODO: maybe need reverse ping checker
            #portfwd = ",hostfwd=udp::67-:67"
            #portfwd += ",hostfwd=udp::68-:68" # icmp port cannot foward
            portfwd = "hostfwd=tcp::80-:80,hostfwd=tcp::443-:443,"
            for (proto, ip, port) in ports:
                if port in [80, 443]:
                    continue
                portfwd += "hostfwd=%(TYPE)s::%(PORT)i-:%(PORT)i," % {"TYPE" : proto, "PORT" : port}

            return "-device %(DEVICE)s,netdev=net%(I)i -netdev user,id=net%(I)i,%(FWD)s" % {'DEVICE': device, 'I': i, "FWD": portfwd[:-1]}
        else:
            return "-device %(DEVICE)s,netdev=net%(I)i -netdev tap,id=net%(I)i,ifname=${TAPDEV_%(TAP_NUM)i},script=no" % { 'I' : i, 'DEVICE' : device, 'TAP_NUM' : tap_num}

def qemuNetworkConfig(arch, network, isUserNetwork, ports):
    output = []
    assigned = []
    interfaceNum = 4
    if arch == "arm" and checkVariable("FIRMAE_NETWORK"):
        interfaceNum = 1

    for i in range(0, interfaceNum):
        for j, n in enumerate(network):
            # need to connect the jth emulated network interface to the corresponding host interface
            if i == ifaceNo(n[1]):
                output.append(qemuArchNetworkConfig(i, j, arch, n, isUserNetwork, ports))
                assigned.append(n)
                break

        # otherwise, put placeholder socket connection
        if len(output) <= i:
            output.append(qemuArchNetworkConfig(i, i, arch, None, isUserNetwork, ports))

    # find unassigned interfaces
    for j, n in enumerate(network[:interfaceNum]):
        if n not in assigned:
            # guess assignment
            print("Warning: Unmatched interface: %s" % (n,))
            output[j] = qemuArchNetworkConfig(j, j, arch, n, isUserNetwork, ports)
            assigned.append(n)

    return ' '.join(output)

def buildConfig(brif, iface, vlans, macs):
    #there should be only one ip
    ip = brif[1]
    br = brif[0]

    #strip vlanid from interface name (e.g., eth2.2 -> eth2)
    dev = iface.split(".")[0]

    #check whether there is a different mac set
    mac = None
    d = dict(macs)
    if br in d:
        mac = d[br]
    elif dev in d:
        mac = d[dev]

    vlan_id = None
    if len(vlans):
        vlan_id = vlans[0]

    return (ip, dev, vlan_id, mac, br)

def convertToHostIp(ip):
    tups = [int(x) for x in ip.split(".")]
    if tups[3] > 1: # sometimes it can has 0 asus FW_RT_AC3100_300438432738
        tups[3] -= 1
    else:
        tups[3] += 1
    return ".".join([str(x) for x in tups])

# iterating the networks
def startNetwork(network):
    template_1 = """
TAPDEV_%(I)i=tap${IID}_%(I)i
HOSTNETDEV_%(I)i=${TAPDEV_%(I)i}
echo "Creating TAP device ${TAPDEV_%(I)i}..."
tunctl -t ${TAPDEV_%(I)i} -u root
"""

    if checkVariable("FIRMAE_NETWORK"):
        template_vlan = """
echo "Initializing VLAN..."
HOSTNETDEV_%(I)i=${TAPDEV_%(I)i}.%(VLANID)i
ip link add link ${TAPDEV_%(I)i} name ${HOSTNETDEV_%(I)i} type vlan id %(VLANID)i
ip link set ${TAPDEV_%(I)i} up
"""

        template_2 = """
echo "Bringing up TAP device..."
ip link set ${HOSTNETDEV_%(I)i} up
ip addr add %(HOSTIP)s/24 dev ${HOSTNETDEV_%(I)i}
"""
    else:
        template_vlan = """
echo "Initializing VLAN..."
HOSTNETDEV_%(I)i=${TAPDEV_%(I)i}.%(VLANID)i
ip link add link ${TAPDEV_%(I)i} name ${HOSTNETDEV_%(I)i} type vlan id %(VLANID)i
ip link set ${HOSTNETDEV_%(I)i} up
"""

        template_2 = """
echo "Bringing up TAP device..."
ip link set ${HOSTNETDEV_%(I)i} up
ip addr add %(HOSTIP)s/24 dev ${HOSTNETDEV_%(I)i}

echo "Adding route to %(GUESTIP)s..."
ip route add %(GUESTIP)s via %(GUESTIP)s dev ${HOSTNETDEV_%(I)i}
"""

    output = []
    for i, (ip, dev, vlan, mac, brif) in enumerate(network):
        output.append(template_1 % {'I' : i})
        if vlan != None:
            output.append(template_vlan % {'I' : i, 'VLANID' : vlan})
        output.append(template_2 % {'I' : i, 'HOSTIP' : convertToHostIp(ip), 'GUESTIP': ip})
    return '\n'.join(output)

def stopNetwork(network):
    template_1 = """
echo "Bringing down TAP device..."
ip link set ${TAPDEV_%(I)i} down
"""

    template_vlan = """
echo "Removing VLAN..."
ip link delete ${HOSTNETDEV_%(I)i}
"""

    template_2 = """
echo "Deleting TAP device ${TAPDEV_%(I)i}..."
tunctl -d ${TAPDEV_%(I)i}
"""

    output = []
    for i, (ip, dev, vlan, mac, brif) in enumerate(network):
        output.append(template_1 % {'I' : i})
        if vlan != None:
            output.append(template_vlan % {'I' : i})
        output.append(template_2 % {'I' : i})
    return '\n'.join(output)

def qemuCmd(iid, network, ports, network_type, arch, endianness, qemuInitValue, isUserNetwork):
    network_bridge = ""
    network_iface = ""
    if arch == "mips":
        qemuEnvVars = ""
        qemuDisk = "-drive if=ide,format=raw,file=${IMAGE}"
        if endianness != "eb" and endianness != "el":
            raise Exception("You didn't specify a valid endianness")
    elif arch == "arm":
        qemuDisk = "-drive if=none,file=${IMAGE},format=raw,id=rootfs -device virtio-blk-device,drive=rootfs"
        if endianness == "el":
            qemuEnvVars = "QEMU_AUDIO_DRV=none"
        elif endianness == "eb":
            raise Exception("armeb currently not supported")
        else:
            raise Exception("You didn't specify a valid endianness")
    else:
        raise Exception("Unsupported architecture")

    for (ip, dev, vlan, mac, brif) in network:
        network_bridge = brif
        network_iface = dev
        break

    return QEMUCMDTEMPLATE % {'IID': iid,
                              'NETWORK_TYPE' : network_type,
                              'NET_BRIDGE' : network_bridge,
                              'NET_INTERFACE' : network_iface,
                              'START_NET' : startNetwork(network),
                              'STOP_NET' : stopNetwork(network),
                              'ARCHEND' : arch + endianness,
                              'QEMU_DISK' : qemuDisk,
                              'QEMU_INIT' : qemuInitValue,
                              'QEMU_NETWORK' : qemuNetworkConfig(arch, network, isUserNetwork, ports),
                              'QEMU_ENV_VARS' : qemuEnvVars}

def getNetworkList(data, ifacesWithIps, macChanges):
    global debug
    networkList = []
    deviceHasBridge = False
    for iwi in ifacesWithIps:
        if iwi[0] == 'lo': # skip local network
            continue
        #find all interfaces that are bridged with that interface
        brifs = findIfacesForBridge(data, iwi[0])
        if debug:
            print("brifs for %s %r" % (iwi[0], brifs))
        for dev in brifs:
            #find vlan_ids for all interfaces in the bridge
            vlans = findVlanInfoForDev(data, dev)
            #create a config for each tuple
            config = buildConfig(iwi, dev, vlans, macChanges)
            if config not in networkList:
                networkList.append(config)
                deviceHasBridge = True

        #if there is no bridge just add the interface
        if not brifs and not deviceHasBridge:
            vlans = findVlanInfoForDev(data, iwi[0])
            config = buildConfig(iwi, iwi[0], vlans, macChanges)
            if config not in networkList:
                networkList.append(config)

    if checkVariable("FIRMAE_NETWORK"):
        return networkList
    else:
        ips = set()
        pruned_network = []
        for n in networkList:
            if n[0] not in ips:
                ips.add(n[0])
                pruned_network.append(n)
            else:
                if debug:
                    print("duplicate ip address for interface: ", n)
        return pruned_network

def readWithException(filePath):
    fileData = ''
    with open(filePath, 'rb') as f:
        while True:
            try:
                line = f.readline().decode()
                if not line:
                    break
                fileData += line
            except:
                fileData += ''

    return fileData

def inferNetwork(iid, arch, endianness, init):
    global SCRIPTDIR
    global SCRATCHDIR
    TIMEOUT = int(os.environ['TIMEOUT'])
    targetDir = SCRATCHDIR + '/' + str(iid)

    loopFile = mountImage(targetDir)

    fileType = subprocess.check_output(["file", "-b", "%s/image/%s" % (targetDir, init)]).decode().strip()
    print("[*] Infer test: %s (%s)" % (init, fileType))

    with open(targetDir + '/image/firmadyne/network_type', 'w') as out:
        out.write("None")

    qemuInitValue = 'rdinit=/firmadyne/preInit.sh'
    if os.path.exists(targetDir + '/service'):
        webService = open(targetDir + '/service').read().strip()
    else:
        webService = None
    print("[*] web service: %s" % webService)
    targetFile = ''
    targetData = ''
    out = None
    if not init.endswith('preInit.sh'): # rcS, preinit
        if fileType.find('ELF') == -1 and fileType.find("symbolic link") == -1: # maybe script
            targetFile = targetDir + '/image/' + init
            targetData = readWithException(targetFile)
            out = open(targetFile, 'a')
        # netgear R6200
        elif fileType.find('ELF') != -1 or fileType.find("symbolic link") != -1:
            qemuInitValue = qemuInitValue[2:] # remove 'rd'
            targetFile = targetDir + '/image/firmadyne/preInit.sh'
            targetData = readWithException(targetFile)
            out = open(targetFile, 'a')
            out.write(init + ' &\n')
    else: # preInit.sh
        out = open(targetDir + '/image/firmadyne/preInit.sh', 'a')

    if out:
        out.write('\n/firmadyne/network.sh &\n')
        out.write('/firmadyne/run_service.sh &\n')
        out.write('/firmadyne/debug.sh\n')
        # trendnet TEW-828DRU_1.0.7.2, etc...
        out.write('/firmadyne/busybox sleep 36000\n')
        out.close()

    umountImage(targetDir, loopFile)

    print("Running firmware %d: terminating after %d secs..." % (iid, TIMEOUT))

    cmd = "timeout --preserve-status --signal SIGINT {0} ".format(TIMEOUT)
    cmd += "{0}/run.{1}.sh \"{2}\" \"{3}\" ".format(SCRIPTDIR,
                                                    arch + endianness,
                                                    iid,
                                                    qemuInitValue)
    cmd += " 2>&1 > /dev/null"
    os.system(cmd)

    loopFile = mountImage(targetDir)
    if not os.path.exists(targetDir + '/image/firmadyne/nvram_files'):
        print("Infer NVRAM default file!\n")
        os.system("{}/inferDefault.py {}".format(SCRIPTDIR, iid))
    umountImage(targetDir, loopFile)

    data = open("%s/qemu.initial.serial.log" % targetDir, 'rb').read()

    ports = findPorts(data, endianness)

    #find interfaces with non loopback ip addresses
    ifacesWithIps = findNonLoInterfaces(data, endianness)
    #find changes of mac addresses for devices
    macChanges = findMacChanges(data, endianness)
    print('[*] Interfaces: %r' % ifacesWithIps)

    networkList = getNetworkList(data, ifacesWithIps, macChanges)
    return qemuInitValue, networkList, targetFile, targetData, ports

def checkNetwork(networkList):
    filterNetworkList = []
    devList = ["eth0", "eth1", "eth2", "eth3"]
    result = "None"

    if checkVariable("FIRMAE_NETWORK"):
        devs = [dev for (ip, dev, vlan, mac, brif) in networkList]
        devs = set(devs)
        ips = [ip for (ip, dev, vlan, mac, brif) in networkList]
        ips = set(ips)
        # check "ethX" and bridge interfaces
        # bridge interface can be named guest-lan1, br0
        # wnr2000v4-V1.0.0.70.zip - mipseb
        # [('192.168.1.1', 'br0', None, None, 'br0'), ('10.0.2.15', 'eth0', None, None, 'br1')]
        # R6900
        # [('192.168.1.1', 'br0', None, None, 'br0'), ('20.45.150.190', 'eth0', None, None, 'eth0')]
        if (len(devs) > 1 and
            any([dev.startswith('eth') for dev in devs]) and
            any([not dev.startswith('eth') for dev in devs])):
            print("[*] Check router")
            # remove dhcp ip address
            networkList = [network for network in networkList if not network[1].startswith("eth")]
        # linksys FW_LAPAC1200_LAPAC1750_1.1.03.000
        # [('192.168.1.252', 'eth0', None, None, 'br0'), ('10.0.2.15', 'eth0', None, None, 'br0')]
        elif (len(ips) > 1 and
              any([ip.startswith("10.0.2.") for ip in ips]) and
              any([not ip.startswith("10.0.2.") for ip in ips])):
            print("[*] Check router")
            # remove dhcp ip address
            networkList = [network for network in networkList if not network[0].startswith("10.0.2.")]

        # br and eth
        if networkList:
            vlanNetworkList = [network for network in networkList if not network[0].endswith(".0.0.0") and network[1].startswith("eth") and network[2] != None]
            ethNetworkList = [network for network in networkList if not network[0].endswith(".0.0.0") and network[1].startswith("eth")]
            invalidEthNetworkList = [network for network in networkList if network[0].endswith(".0.0.0") and network[1].startswith("eth")]
            brNetworkList = [network for network in networkList if not network[0].endswith(".0.0.0") and not network[1].startswith("eth")]
            invalidBrNetworkList = [network for network in networkList if network[0].endswith(".0.0.0") and not network[1].startswith("eth")]
            if vlanNetworkList:
                print("has vlan ethernet")
                filterNetworkList = vlanNetworkList
                result = "normal"
            elif ethNetworkList:
                print("has ethernet")
                filterNetworkList = ethNetworkList
                result = "normal"
            elif invalidEthNetworkList:
                print("has ethernet and invalid IP")
                for (ip, dev, vlan, mac, brif) in invalidEthNetworkList:
                    filterNetworkList.append(('192.168.0.1', dev, vlan, mac, brif))
                result = "reload"
            elif brNetworkList:
                print("only has bridge interface")
                for (ip, dev, vlan, mac, brif) in brNetworkList:
                    if devList:
                        dev = devList.pop(0)
                        filterNetworkList.append((ip, dev, vlan, mac, brif))
                result = "bridge"
            elif invalidBrNetworkList:
                print("only has bridge interface and invalid IP")
                for (ip, dev, vlan, mac, brif) in invalidBrNetworkList:
                    if devList:
                        dev = devList.pop(0)
                        filterNetworkList.append(('192.168.0.1', dev, vlan, mac, brif))
                result = "bridgereload"

        else:
            print("[*] no network interface: bring up default network")
            filterNetworkList.append(('192.168.0.1', 'eth0', None, None, "br0"))
            result = "default"
    else: # if checkVariable("FIRMAE_NETWORK"):
        filterNetworkList = networkList

    return filterNetworkList, result # (network_type)

def process(iid, arch, endianness, makeQemuCmd=False, outfile=None):
    success = False

    global SCRIPTDIR
    global SCRATCHDIR

    for init in open(SCRATCHDIR + "/" + str(iid) + "/init").read().split('\n')[:-1]:
        with open(SCRATCHDIR + "/" + str(iid) + "/current_init", 'w') as out:
            out.write(init)
        qemuInitValue, networkList, targetFile, targetData, ports = inferNetwork(iid, arch, endianness, init)

        print("[*] ports: %r" % ports)
        # check network interfaces and add script in the file system
        # return the fixed network interface
        print("[*] networkInfo: %r" % networkList)
        filterNetworkList, network_type = checkNetwork(networkList)

        print("[*] filter network info: %r" % filterNetworkList)

        # filter ip
        # some firmware uses multiple network interfaces for one bridge
        # netgear WNDR3400v2-V1.0.0.54_1.0.82.zip - check only one IP
        # asus FW_RT_AC87U_300438250702
        # [('192.168.1.1', 'eth0', None, None), ('169.254.39.3', 'eth1', None, None), ('169.254.39.1', 'eth2', None, None), ('169.254.39.166', 'eth3', None, None)]

        if filterNetworkList:
            ips = [ip for (ip, dev, vlan, mac, brif) in filterNetworkList]
            ips = set(ips)
            with open(SCRATCHDIR + "/" + str(iid) + "/ip_num", 'w') as out:
                out.write(str(len(ips)))

            for idx, ip in enumerate(ips):
                with open(SCRATCHDIR + "/" + str(iid) + "/ip." + str(idx), 'w') as out:
                    out.write(str(ip))

            isUserNetwork = any(isDhcpIp(ip) for ip in ips)
            with open(SCRATCHDIR + "/" + str(iid) + "/isDhcp", "w") as out:
                if isUserNetwork:
                    out.write("true")
                else:
                    out.write("false")

            qemuCommandLine = qemuCmd(iid,
                                      filterNetworkList,
                                      ports,
                                      network_type,
                                      arch,
                                      endianness,
                                      qemuInitValue,
                                      isUserNetwork)

            with open(outfile, "w") as out:
                out.write(qemuCommandLine)
            os.chmod(outfile, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

            os.system('./scripts/test_emulation.sh {} {}'.format(iid, arch + endianness))

            if (os.path.exists(SCRATCHDIR + '/' + str(iid) + '/web') and
                open(SCRATCHDIR + '/' + str(iid) + '/web').read().strip() == 'true'):
                success = True
                break

        # restore infer network data
        # targetData is '' when init is preInit.sh
        if targetData != '':
            targetDir = SCRATCHDIR + '/' + str(iid)
            loopFile = mountImage(targetDir)
            with open(targetFile, 'w') as out:
                out.write(targetData)
            umountImage(targetDir, loopFile)

    return success

def archEnd(value):
    arch = None
    end = None

    tmp = value.lower()
    if tmp.startswith("mips"):
        arch = "mips"
    elif tmp.startswith("arm"):
        arch = "arm"
    if tmp.endswith("el"):
        end = "el"
    elif tmp.endswith("eb"):
        end = "eb"
    return (arch, end)

def getWorkDir():
    if os.path.isfile("./firmae.config"):
        return os.getcwd()
    elif os.path.isfile("../firmae.config"):
        path = os.getcwd()
        return path[:path.rfind('/')]
    else:
        return None

def main():
    makeQemuCmd = False
    iid = None
    outfile = None
    arch = None
    endianness = None
    workDir = getWorkDir()
    if not workDir:
        raise Exception("Can't find firmae.config file")

    global SCRATCHDIR
    global SCRIPTDIR
    SCRATCHDIR = workDir + '/scratch'
    SCRIPTDIR = workDir + '/scripts'
    (opts, argv) = getopt.getopt(sys.argv[1:], 'i:a:oqd')
    for (k, v) in opts:
        if k == '-d':
            global debug
            debug += 1
        if k == '-q':
            makeQemuCmd = True
        if k == '-i':
            iid = int(v)
        if k == '-o':
            outfile = True
        if k == '-a':
            (arch, endianness) = archEnd(v)

    if not arch or not endianness:
        raise Exception("Either arch or endianness not found try mipsel/mipseb/armel/armeb")

    if outfile and iid:
        outfile = """%s/%i/run.sh""" % (SCRATCHDIR, iid)
    if debug:
        print("processing %i" % iid)
    process(iid, arch, endianness, makeQemuCmd, outfile)

if __name__ == "__main__":
    main()
