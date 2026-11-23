import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

cmd = """python3 -c "
path = '/serverhive5/eiarf/lineage-22/kernel/sony/msm8974/include/linux/fs.h'
with open(path, 'r') as f:
    c = f.read()

target = '#define SEEK_MAX\\tSEEK_HOLE'
rep = '''#define SEEK_MAX\\tSEEK_HOLE

#ifndef RENAME_NOREPLACE
#define RENAME_NOREPLACE\\t(1 << 0)\\t/* Don\\x27t overwrite target */
#define RENAME_EXCHANGE\\t\\t(1 << 1)\\t/* Exchange source and dest */
#define RENAME_WHITEOUT\\t\\t(1 << 2)\\t/* Whiteout source */
#endif'''

# reset first
lines = c.splitlines()
cleaned_lines = [l for l in lines if 'RENAME_' not in l and '#ifndef RENAME' not in l and '#endif' not in l or 'SEEK_MAX' in l]
# Just use git checkout
"
"""

reset_and_patch = """bash -c '
cd /serverhive5/eiarf/lineage-22/kernel/sony/msm8974
git checkout include/linux/fs.h
python3 -c "
path = \\"include/linux/fs.h\\"
with open(path, \\"r\\") as f:
    c = f.read()
target = \\"#define SEEK_MAX\\tSEEK_HOLE\\"
rep = \\"\\"\\"#define SEEK_MAX\\tSEEK_HOLE

#ifndef RENAME_NOREPLACE
#define RENAME_NOREPLACE\\t(1 << 0)\\t/* Dont overwrite target */
#define RENAME_EXCHANGE\\t\\t(1 << 1)\\t/* Exchange source and dest */
#define RENAME_WHITEOUT\\t\\t(1 << 2)\\t/* Whiteout source */
#endif\\"\\"\\"
if target in c:
    with open(path, \\"w\\") as f:
        f.write(c.replace(target, rep))
    print(\\"fs.h cleanly patched\\")
"
'"""

stdin, stdout, stderr = ssh.exec_command(reset_and_patch)
print("STDOUT:\n" + stdout.read().decode())
print("STDERR:\n" + stderr.read().decode())
ssh.close()
