BUSYBOX="/busybox"

${BUSYBOX} touch /firmadyne/init

if (${FIRMAE_BOOT}); then
  arr=()
  if [ -e /kernelInit ]; then
    for FILE in `${BUSYBOX} strings ./kernelInit`
    do
      FULL_PATH=`${BUSYBOX} echo ${FILE} | ${BUSYBOX} awk '{split($0,a,"="); print a[2]}'`
      arr+=("${FULL_PATH}")
    done
  fi
  # kernel not handle this program
  for FILE in `${BUSYBOX} find / -name "preinitMT" -o -name "preinit" -o -name "rcS"`
  do
    arr+=(${FILE})
  done

  if (( ${#arr[@]} )); then
    # convert to the unique array following the original order
    uniq_arr=($(${BUSYBOX} tr ' ' '\n' <<< "${arr[@]}" | ${BUSYBOX} awk '!u[$0]++' | ${BUSYBOX} tr '\n' ' '))
    for FILE in "${uniq_arr[@]}"
    do
      if [ -d ${FILE} ]; then
        continue
      fi
      if [ ! -e ${FILE} ]; then # can't found original file (symbolic link or just file)
        if [ -h ${FILE} ]; then # remove old symbolic link
          ${BUSYBOX} rm ${FILE}
        fi
        # find original program from binary directories
        FILE_NAME=`${BUSYBOX} basename ${FILE}`
        if (${BUSYBOX} find /bin /sbin /usr/sbin /usr/sbin -type f -exec ${BUSYBOX} grep -qr ${FILE_NAME} {} \;); then
          TARGET_FILE=`${BUSYBOX} find /bin /sbin /usr/sbin /usr/sbin -type f -exec ${BUSYBOX} egrep -rl ${FILE_NAME} {} \; | ${BUSYBOX} head -1`
          ${BUSYBOX} ln -s ${TARGET_FILE} ${FILE}
        else
          continue
        fi
      fi
      if [ -e ${FILE} ]; then
        ${BUSYBOX} echo ${FILE} >> /firmadyne/init
      fi
    done
  fi
fi

${BUSYBOX} echo '/firmadyne/preInit.sh' >> /firmadyne/init

if (${FIRMAE_ETC}); then
    if [ -e /etc/init.d/uhttpd ]; then
        echo -n "/etc/init.d/uhttpd start" > /firmadyne/service
        echo -n "uhttpd" > /firmadyne/service_name
    elif [ -e /usr/bin/httpd ]; then
        echo -n "/usr/bin/httpd" > /firmadyne/service
        echo -n "httpd" > /firmadyne/service_name
    elif [ -e /usr/sbin/httpd ]; then
        echo -n "/usr/sbin/httpd" > /firmadyne/service
        echo -n "httpd" > /firmadyne/service_name
    elif [ -e /bin/goahead ]; then
        echo -n "/bin/goahead" > /firmadyne/service
        echo -n "goahead" > /firmadyne/service_name
    elif [ -e /bin/alphapd ]; then
        echo -n "/bin/alphapd" > /firmadyne/service
        echo -n "alphapd" > /firmadyne/service_name
    elif [ -e /bin/boa ]; then
        echo -n "/bin/boa" > /firmadyne/service
        echo -n "boa" > /firmadyne/service_name
    elif [ -e /usr/sbin/lighttpd ]; then # for Ubiquiti firmwares
        echo -n "/usr/sbin/lighttpd -f /etc/lighttpd/lighttpd.conf" > /firmadyne/service
        echo -n "lighttpd" > /firmadyne/service_name
    fi
fi
