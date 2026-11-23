import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

cmd = """python3 -c "
path = '/serverhive5/eiarf/lineage-22/kernel/sony/msm8974/include/linux/syscalls.h'
with open(path, 'r') as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    if 'asmlinkage long sys_renameat2' in line:
        continue
    new_lines.append(line)
    if 'int newdfd, const char __user * newname);' in line:
        new_lines.append('asmlinkage long sys_renameat2(int olddfd, const char __user *oldname, int newdfd, const char __user *newname, unsigned int flags);\\n')
with open(path, 'w') as f:
    f.writelines(new_lines)
print('syscalls.h cleanly fixed')
"
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
