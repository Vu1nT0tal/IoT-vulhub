#!/usr/bin/env python3

import os.path
import subprocess
import sys
import time
import telnetlib
from socket import *


class firmadyne_helper():
    def __init__(self, iid):
        self.iid = int(iid)
        self.targetName = open('./scratch/%d/name' % iid).read().strip()
        self.targetIP = open('./scratch/%d/ip' % iid).read().strip()
        self.telnetInit = False

    def show_info(self):
        print('[*] firmware - %s' % self.targetName)
        print('[*] IP - %s' % self.targetIP)

    def connect(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        print('[*] connecting...')
        self.sock.connect((self.targetIP, 31337))
        print('[*] connected')

    def sendrecv(self, cmd):
        self.sock.send(cmd.encode())
        time.sleep(1)
        return self.sock.recv(2048).decode()

    def send(self, cmd):
        self.sock.send(cmd.encode())

    def initalize_telnet(self):
        for command in ['/firmadyne/busybox mkdir -p /proc',
                        '/firmadyne/busybox ln -sf /proc/mounts /etc/mtab',
                        '/firmadyne/busybox mkdir -p /dev/pts',
                        '/firmadyne/busybox mount -t devpts devpts /dev/pts']:
            self.send(command + '\n')
            time.sleep(0.1)
        self.telnetInit = True

    def connect_shell(self):
        if not self.telnetInit:
            self.initalize_telnet()
        subprocess.call(['telnet',self.targetIP,'31338'])

    def show_processlist(self):
        print(self.sendrecv('ps\n'))

    def tcpdump(self):
        argument = input('tcpdump -i tap%d_0 ' % self.iid)
        os.system('tcpdump -i tap%d_0 %s' % (self.iid, argument))

    def file_transfer(self, target_filepath):
        file_name = os.path.basename(target_filepath)
        self.send('/firmadyne/busybox nc -lp 31339 > /firmadyne/%s &\n' % file_name)
        time.sleep(1)
        os.system('cat ' + target_filepath + ' | nc ' + self.targetIP + ' 31339 &')
        while True:
            if self.sendrecv('ps\n').find('31339') != -1:
                time.sleep(1)
            else:
                break
        print('[*] transfer complete!')

    def run_gdbserver(self, PID, PORT=1337):
        print('[+] gdbserver at %s:%d attach on %s' % (self.targetIP, PORT, PID))
        print('[+] run target "remote %s:%d" in host gdb' % (self.targetIP, PORT))
        self.send('/firmadyne/gdbserver %s:%d --attach %s\n'%(self.targetIP, PORT, PID))

if __name__ == '__main__':
    if sys.version[:1] != '3':
        print('error : python version should be 3.X.X')
        exit(-1)
    elif len(sys.argv) != 2:
        print('usage: %s [iid]' % sys.argv[0])
        exit(-1)
    elif not sys.argv[1].isnumeric():
        print('error : iid should be number')
        exit(-1)
    elif not os.path.isdir('./scratch/%s'%(sys.argv[1])):
        print('error : invaild iid.')
        exit(-1)

    #initialize helper
    fh = firmadyne_helper(int(sys.argv[1]))
    fh.show_info()
    fh.connect()

    def menu():
        print('------------------------------')
        print('  Firmadyne-EX Debugger v1.0')
        print('------------------------------')
        print('1. connect to shell')
        print('2. tcpdump')
        print('3. run gdbserver')
        print('4. file transfer')
        print('5. exit')

    while 1:
        menu()
        try:
            select = int(input('> '))
        except KeyboardInterrupt:
            break
        except:
            select = ''
            pass

        if select == 1:
            fh.connect_shell()
        elif select == 2:
            fh.tcpdump()
        elif select == 3:
            fh.show_processlist()
            try:
                PID = input('[+] target pid : ')
            except KeyboardInterrupt:
                pass
            else:
                fh.run_gdbserver(PID)
        elif select == 4:
            target_filepath = input('[+] target file path : ')
            fh.file_transfer(target_filepath)
        elif select == 5:
            break
        else:
            print('error : invaild selection')
        print('\n')
