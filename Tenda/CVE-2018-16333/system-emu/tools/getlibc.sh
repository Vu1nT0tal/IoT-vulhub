#!/bin/bash

cat /proc/`ps -ef | grep -v grep | grep httpd | awk '{print $1}'`/maps | grep '/lib/libc.so'
