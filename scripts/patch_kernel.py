import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

remote_script = r"""#!/bin/bash
set -e
KDIR=/serverhive5/eiarf/lineage-22/kernel/sony/msm8974

# 1. arch/arm/include/asm/unistd.h
if ! grep -q '__NR_renameat2' $KDIR/arch/arm/include/asm/unistd.h; then
    sed -i '/__NR_process_vm_writev/a #define __NR_renameat2\t\t\t(__NR_SYSCALL_BASE+382)' $KDIR/arch/arm/include/asm/unistd.h
fi

# 2. include/asm-generic/unistd.h
if ! grep -q '__NR_renameat2' $KDIR/include/asm-generic/unistd.h; then
    sed -i '/#define __NR_seccomp 277/i #define __NR_renameat2 276\n__SYSCALL(__NR_renameat2, sys_renameat2)' $KDIR/include/asm-generic/unistd.h
fi

# 3. arch/arm/kernel/calls.S (replace the 3rd sys_ni_syscall after 380)
python3 -c "
path = '$KDIR/arch/arm/kernel/calls.S'
with open(path, 'r') as f:
    content = f.read()
target = '/* 380 */\tCALL(sys_ni_syscall)\n\t\tCALL(sys_ni_syscall)\n\t\tCALL(sys_ni_syscall)'
replacement = '/* 380 */\tCALL(sys_ni_syscall)\n\t\tCALL(sys_ni_syscall)\n\t\tCALL(sys_renameat2)'
if target in content:
    with open(path, 'w') as f:
        f.write(content.replace(target, replacement))
    print('calls.S patched successfully')
elif 'CALL(sys_renameat2)' in content:
    print('calls.S already patched')
else:
    print('Target not found in calls.S!')
"

# 4. include/linux/syscalls.h
if ! grep -q 'sys_renameat2' $KDIR/include/linux/syscalls.h; then
    sed -i '/asmlinkage long sys_renameat(/a asmlinkage long sys_renameat2(int olddfd, const char __user *oldname, int newdfd, const char __user *newname, unsigned int flags);' $KDIR/include/linux/syscalls.h
fi

# 5. include/linux/fs.h (RENAME_NOREPLACE definitions)
if ! grep -q 'RENAME_NOREPLACE' $KDIR/include/linux/fs.h; then
    sed -i '/#define SEEK_MAX/a \\n#ifndef RENAME_NOREPLACE\\n#define RENAME_NOREPLACE\t(1 << 0)\t/* Dont overwrite target */\\n#define RENAME_EXCHANGE\t\t(1 << 1)\t/* Exchange source and dest */\\n#define RENAME_WHITEOUT\t\t(1 << 2)\t/* Whiteout source */\\n#endif' $KDIR/include/linux/fs.h
fi

# 6. fs/namei.c
python3 -c "
path = '$KDIR/fs/namei.c'
with open(path, 'r') as f:
    c = f.read()

old_decl = 'SYSCALL_DEFINE4(renameat, int, olddfd, const char __user *, oldname,\n\t\tint, newdfd, const char __user *, newname)'
new_decl = 'SYSCALL_DEFINE5(renameat2, int, olddfd, const char __user *, oldname,\n\t\tint, newdfd, const char __user *, newname, unsigned int, flags)\n{\n\tstruct dentry *old_dir, *new_dir;\n\tstruct dentry *old_dentry, *new_dentry;\n\tstruct dentry *trap;\n\tstruct nameidata oldnd, newnd;\n\tstruct filename *from;\n\tstruct filename *to;\n\tint error;\n\n\tif (flags & ~RENAME_NOREPLACE)\n\t\treturn -EINVAL;'

if old_decl in c:
    old_block = old_decl + '\n{\n\tstruct dentry *old_dir, *new_dir;\n\tstruct dentry *old_dentry, *new_dentry;\n\tstruct dentry *trap;\n\tstruct nameidata oldnd, newnd;\n\tstruct filename *from;\n\tstruct filename *to;\n\tint error;'
    c = c.replace(old_block, new_decl)
    
    lookup_target = 'new_dentry = lookup_hash(&newnd);\n\terror = PTR_ERR(new_dentry);\n\tif (IS_ERR(new_dentry))\n\t\tgoto exit4;\n\t/* target should not be an ancestor of source */\n\terror = -ENOTEMPTY;\n\tif (new_dentry == trap)\n\t\tgoto exit5;'
    lookup_replacement = lookup_target + '\n\n\terror = -EEXIST;\n\tif ((flags & RENAME_NOREPLACE) && new_dentry->d_inode)\n\t\tgoto exit5;'
    c = c.replace(lookup_target, lookup_replacement)
    
    c = c.replace('\treturn error;\n}\n\nSYSCALL_DEFINE2(rename,', '\treturn error;\n}\n\nSYSCALL_DEFINE4(renameat, int, olddfd, const char __user *, oldname,\n\t\tint, newdfd, const char __user *, newname)\n{\n\treturn sys_renameat2(olddfd, oldname, newdfd, newname, 0);\n}\n\nSYSCALL_DEFINE2(rename,')
    with open(path, 'w') as f:
        f.write(c)
    print('fs/namei.c patched successfully')
elif 'SYSCALL_DEFINE5(renameat2' in c:
    print('fs/namei.c already patched')
else:
    print('Could not match renameat in fs/namei.c')
"

# 7. defconfig: Add ram_console & persistent_ram
DEFCONFIG=$KDIR/arch/arm/configs/lineageos_rhine_amami_row_defconfig
for opt in "CONFIG_ANDROID_PERSISTENT_RAM=y" "CONFIG_ANDROID_RAM_CONSOLE=y" "CONFIG_ANDROID_RAM_CONSOLE_ENABLE_VERBOSE=y"; do
    if ! grep -q "$opt" $DEFCONFIG; then
        echo "$opt" >> $DEFCONFIG
    fi
done

echo "All kernel patches applied successfully!"
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/patch_kernel.sh', 'w') as f:
    f.write(remote_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('bash /tmp/patch_kernel.sh')
print("STDOUT:\n" + stdout.read().decode())
print("STDERR:\n" + stderr.read().decode())
ssh.close()
