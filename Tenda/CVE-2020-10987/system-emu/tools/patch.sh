#!/bin/bash

printf '\x01\x30\xa0\xe3' | dd of=/bin/httpd bs=1 count=4 conv=notrunc seek=156944
printf '\x01\x30\xa0\xe3' | dd of=/bin/httpd bs=1 count=4 conv=notrunc seek=156980
printf '\x00\x30\xa0\xe3' | dd of=/bin/httpd bs=1 count=4 conv=notrunc seek=390808
