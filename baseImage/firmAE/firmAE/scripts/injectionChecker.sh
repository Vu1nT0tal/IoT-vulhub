#!/firmadyne/sh

/firmadyne/busybox date >> /firmadyne/os_cmd_injection_log
/firmadyne/busybox env >> /firmadyne/os_cmd_injection_log
if [ -e /proc/self/stat ];then
  /firmadyne/busybox cat /proc/self/stat >> /firmadyne/os_cmd_injection_log
fi
/firmadyne/busybox echo "" >> /firmadyne/os_cmd_injection_log
