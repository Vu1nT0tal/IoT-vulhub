#!/firmadyne/sh

BUSYBOX=/firmadyne/busybox
BINARY=`${BUSYBOX} cat /firmadyne/service`
BINARY_NAME=`${BUSYBOX} basename ${BINARY}`

if (${FIRMAE_ETC}); then
  ${BUSYBOX} sleep 120
  $BINARY &

  while (true); do
      ${BUSYBOX} sleep 10
      if ( ! (${BUSYBOX} ps | ${BUSYBOX} grep -v grep | ${BUSYBOX} grep -sqi ${BINARY_NAME}) ); then
          $BINARY &
      fi
  done
fi
