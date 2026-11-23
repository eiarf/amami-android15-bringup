import paramiko
import sys

def run_ssh(cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("waffle.serverhive.in", port=22, username="eiarf", password="ElectricJaguar5659")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    client.close()
    return exit_code, out, err

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "whoami"
    code, out, err = run_ssh(cmd)
    print(f"EXIT CODE: {code}")
    if out:
        print("STDOUT:\n" + out)
    if err:
        print("STDERR:\n" + err)
