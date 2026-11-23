import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

cmd = """python3 -c "
import struct
with open('/serverhive5/eiarf/lineage-22/out/target/product/amami/boot_test_rev4.img', 'rb') as f:
    h = f.read(2048)
k_sz, k_addr, r_sz, r_addr, s_sz, s_addr, tags_addr, page_sz, unused, os_ver = struct.unpack('<IIIIIIIIII', h[8:48])
cmdline = h[64:576].split(b'\\x00')[0].decode('utf-8')
print('k_sz:', k_sz, 'k_addr:', hex(k_addr))
print('r_sz:', r_sz, 'r_addr:', hex(r_addr))
print('s_sz:', s_sz, 's_addr:', hex(s_addr))
print('tags_addr:', hex(tags_addr))
print('page_sz:', page_sz)
print('cmdline:', cmdline)
" """

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
