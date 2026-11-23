import paramiko
import sys
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

cmd = """bash -c '
set -e
cd /serverhive5/eiarf/lineage-22
source build/envsetup.sh
lunch lineage_amami-bp1a-userdebug
ulimit -s unlimited && ulimit -n 65536
mka bootimage
'"""

print("Starting mka bootimage on server...")
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

# Stream stdout in real time
for line in iter(stdout.readline, ""):
    print(line, end="")

exit_code = stdout.channel.recv_exit_status()
print(f"\nFinished with exit code: {exit_code}")
ssh.close()
sys.exit(exit_code)
