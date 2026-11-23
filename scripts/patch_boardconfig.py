import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

patch_script = """python3 -c "
path = '/serverhive5/eiarf/lineage-22/device/sony/rhine-common/BoardConfigCommon.mk'
with open(path, 'r') as f:
    content = f.read()

old_block = '''BOARD_KERNEL_IMAGE_NAME := zImage-dtb
BOARD_KERNEL_BASE     := 0x00000000
BOARD_KERNEL_PAGESIZE := 2048
BOARD_KERNEL_CMDLINE  := androidboot.hardware=qcom user_debug=31 msm_rtb.filter=0x3b7 ehci-hcd.park=3 androidboot.bootdevice=msm_sdcc.1 vmalloc=300M dwc3.maximum_speed=high dwc3_msm.prop_chg_detect=Y
BOARD_KERNEL_CMDLINE  += androidboot.selinux=permissive
BOARD_KERNEL_CMDLINE  += androidboot.first_stage_console=1 earlyprintk
BOARD_MKBOOTIMG_ARGS  := --ramdisk_offset 0x02000000 --tags_offset 0x01E00000'''

new_block = '''BOARD_KERNEL_IMAGE_NAME := zImage-dtb
BOARD_KERNEL_BASE     := 0x00000000
BOARD_KERNEL_PAGESIZE := 2048
BOARD_KERNEL_CMDLINE  := androidboot.hardware=qcom user_debug=31 msm_rtb.filter=0x37 ehci-hcd.park=3 androidboot.bootdevice=msm_sdcc.1 dwc3.maximum_speed=high dwc3_msm.prop_chg_detect=Y androidboot.selinux=permissive
BOARD_MKBOOTIMG_ARGS  := --ramdisk_offset 0x01000000 --tags_offset 0x01E00000'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(path, 'w') as f:
        f.write(content)
    print('SUCCESS: BoardConfigCommon.mk patched')
else:
    print('WARNING: old_block not found in BoardConfigCommon.mk')
" """

stdin, stdout, stderr = ssh.exec_command(patch_script)
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
