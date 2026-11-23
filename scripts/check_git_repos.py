import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('waffle.serverhive.in', port=22, username='eiarf', password='ElectricJaguar5659')

cmd = """bash -c '
repos=(
    "device/sony/amami"
    "device/sony/rhine-common"
    "device/sony/msm8974-common"
    "kernel/sony/msm8974"
    "system/bpf"
    "hardware/qcom-caf/msm8974/display"
    ".repo/local_manifests"
)

base="/serverhive5/eiarf/lineage-22"
for r in "${repos[@]}"; do
    p="$base/$r"
    if [ -d "$p" ]; then
        echo "=== $r ==="
        cd "$p"
        git status -s
        git remote -v
    fi
done
'"""

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
