#!/bin/bash

/etc/init.d/ssh start
tunctl -t tap0
ifconfig tap0 192.168.2.1/24

cd /root/images

/usr/bin/expect<<EOF
set timeout 10000
spawn qemu-system-arm -M versatilepb -kernel vmlinuz-3.2.0-4-versatile -initrd initrd.img-3.2.0-4-versatile -hda debian_wheezy_armel_standard.qcow2 -append "root=/dev/sda1" -net nic -net tap,ifname=tap0,script=no,downscript=no -nographic

expect "debian-armel login:"
send "root\r"
expect "Password:"
send "root\r"

expect "root@debian-armel:~# "
send "ifconfig eth0 192.168.2.2/24\r"

#expect "root@debian-armel:~# "
#send "echo 0 > /proc/sys/kernel/randomize_va_space\r"

expect "root@debian-armel:~# "
send "scp root@192.168.2.1:/root/squashfs-root.tar.gz /root/squashfs-root.tar.gz\r"
expect {
    "(yes/no)? " { send "yes\r"; exp_continue }
    "password: " { send "root\r" }
}

expect "root@debian-armel:~# "
send "tar xzf squashfs-root.tar.gz && rm squashfs-root.tar.gz\r"
expect "root@debian-armel:~# "
send "echo 127.0.0.1 debian-armel localhost > ./squashfs-root/etc/hosts\r"
expect "root@debian-armel:~# "
send "mount -o bind /dev ./squashfs-root/dev && mount -t proc /proc ./squashfs-root/proc\r"

expect "root@debian-armel:~# "
send "scp -r root@192.168.2.1:/root/tools /root/squashfs-root/tools\r"
expect {
    "(yes/no)? " { send "yes\r"; exp_continue }
    "password: " { send "root\r" }
}

expect "root@debian-armel:~# "
send "chroot squashfs-root/ sh\r"
expect "# "
send "/usr/sbin/httpd\r"

expect eof
EOF

#send "./tools/gdbserver --attach :1234 `ps | grep -v grep | grep httpd | awk '{print $1}'`"
