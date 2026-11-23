import paramiko
import os
import hashlib

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

remote_file = '/serverhive5/eiarf/lineage-22/out/target/product/amami/boot.img'
local_file = 'D:/z1c-a15/out/boot.img'

print(f"Downloading {remote_file} to {local_file}...")
sftp = ssh.open_sftp()
sftp.get(remote_file, local_file)
sftp.close()
ssh.close()

size = os.path.getsize(local_file)
with open(local_file, 'rb') as f:
    sha = hashlib.sha256(f.read()).hexdigest()

print(f"Downloaded successfully: {size:,} bytes")
print(f"SHA-256: {sha}")
