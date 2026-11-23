import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

remote_script = r"""#!/bin/bash
set -e
DEVDIR=/serverhive5/eiarf/lineage-22/device/sony/rhine-common

# 1. rhine.mk
python3 -c "
path = '$DEVDIR/rhine.mk'
with open(path, 'r') as f:
    c = f.read()

target = '\$(COMMON_PATH)/rootdir/fstab.qcom:root/fstab.qcom \\\\'
replacement = '''\$(COMMON_PATH)/rootdir/fstab.qcom:root/fstab.qcom \\\\
    \$(COMMON_PATH)/rootdir/fstab.qcom:\$(TARGET_COPY_OUT_RAMDISK)/fstab.qcom \\\\
    \$(COMMON_PATH)/rootdir/fstab.qcom:\$(TARGET_COPY_OUT_RAMDISK)/first_stage_ramdisk/fstab.qcom \\\\
    \$(COMMON_PATH)/rootdir/fstab.qcom:\$(TARGET_COPY_OUT_RAMDISK)/first_stage_ramdisk/system/etc/fstab.qcom \\\\
    \$(COMMON_PATH)/rootdir/fstab.qcom:\$(TARGET_COPY_OUT_VENDOR)/etc/fstab.qcom \\\\'''

if target in c:
    c = c.replace(target, replacement)
    with open(path, 'w') as f:
        f.write(c)
    print('rhine.mk patched successfully')
elif 'TARGET_COPY_OUT_RAMDISK' in c:
    print('rhine.mk already patched')
else:
    print('Target not found in rhine.mk')
"

# 2. fstab.qcom: add /system entry
python3 -c "
path = '$DEVDIR/rootdir/fstab.qcom'
with open(path, 'r') as f:
    c = f.read()

sys_entry = '/dev/block/platform/msm_sdcc.1/by-name/system       /system    ext4  ro,barrier=1,discard                                                      wait,first_stage_mount'

if '/by-name/system' not in c:
    marker = '#       /proc/device-tree/firmware/android/fstab/system'
    if marker in c:
        c = c.replace(marker, marker + '\n\n' + sys_entry)
        with open(path, 'w') as f:
            f.write(c)
        print('fstab.qcom patched successfully')
    else:
        print('Marker not found in fstab.qcom')
else:
    print('fstab.qcom already contains /by-name/system')
"

# 3. BoardConfigCommon.mk: add early debugging cmdline
python3 -c "
path = '$DEVDIR/BoardConfigCommon.mk'
with open(path, 'r') as f:
    c = f.read()

opt = 'BOARD_KERNEL_CMDLINE  += androidboot.first_stage_console=1 earlyprintk'
if opt not in c:
    c = c.replace('BOARD_KERNEL_CMDLINE  += androidboot.selinux=permissive', 'BOARD_KERNEL_CMDLINE  += androidboot.selinux=permissive\n' + opt)
    with open(path, 'w') as f:
        f.write(c)
    print('BoardConfigCommon.mk patched successfully')
else:
    print('BoardConfigCommon.mk already patched')
"

echo "Device tree patches applied!"
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/patch_device.sh', 'w') as f:
    f.write(remote_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('bash /tmp/patch_device.sh')
print("STDOUT:\n" + stdout.read().decode())
print("STDERR:\n" + stderr.read().decode())
ssh.close()
