import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

remote_script = r"""#!/bin/bash
set -e
KDIR=/serverhive5/eiarf/lineage-22/kernel/sony/msm8974
DEVDIR=/serverhive5/eiarf/lineage-22/device/sony/rhine-common

# 1. Update defconfig
DEFCONFIG=$KDIR/arch/arm/configs/lineageos_rhine_amami_row_defconfig

python3 -c "
path = '$DEFCONFIG'
with open(path, 'r') as f:
    c = f.read()

opts = [
    'CONFIG_ARM_APPENDED_DTB=y',
    'CONFIG_ARM_ATAG_DTB_COMPAT=y',
    'CONFIG_BUILD_ARM_APPENDED_DTB_IMAGE=y',
    'CONFIG_BUILD_ARM_APPENDED_DTB_IMAGE_NAMES=\"msm8974-v2.0-1-rhine_amami_row msm8974-v2.2-rhine_amami_row\"'
]

lines = c.splitlines()
new_lines = []
for l in lines:
    if any(opt.split('=')[0] in l for opt in opts):
        continue
    new_lines.append(l)

new_lines.extend(opts)
with open(path, 'w') as f:
    f.write('\n'.join(new_lines) + '\n')
print('defconfig updated with appended dtb options')
"

# 2. Update BoardConfigCommon.mk
python3 -c "
path = '$DEVDIR/BoardConfigCommon.mk'
with open(path, 'r') as f:
    c = f.read()

c = c.replace('BOARD_KERNEL_IMAGE_NAME := zImage', 'BOARD_KERNEL_IMAGE_NAME := zImage-dtb')
c = c.replace('BOARD_KERNEL_SEPARATED_DT := true', '# BOARD_KERNEL_SEPARATED_DT := true')

with open(path, 'w') as f:
    f.write(c)
print('BoardConfigCommon.mk updated to use zImage-dtb')
"

echo "Done fixing appended DTB config!"
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/fix_appended_dtb.sh', 'w') as f:
    f.write(remote_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('bash /tmp/fix_appended_dtb.sh')
print("STDOUT:\n" + stdout.read().decode())
print("STDERR:\n" + stderr.read().decode())
ssh.close()
