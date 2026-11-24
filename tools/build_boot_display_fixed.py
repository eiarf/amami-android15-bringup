import struct
import hashlib
import sys
sys.path.append(r'C:\Users\Angger\.gemini\antigravity\brain\ea5e589c-b40b-4feb-a749-f96e6a7e88f8\scratch')
from test_fdt import parse_fdt, serialize_fdt

orig_boot_path = r"D:\Custom Rom's Stuff\Project Custom Rom Sony Xperia Z1 Compact\boot.img"
with open(orig_boot_path, 'rb') as f:
    boot_data = bytearray(f.read())

hdr = boot_data[:2048]
k_sz, k_addr, r_sz, r_addr, s_sz, s_addr, t_addr, page = struct.unpack('<8I', hdr[8:40])

def page_align(val, page):
    return (val + page - 1) // page * page

k_off = page
r_off = k_off + page_align(k_sz, page)

kernel_payload = boot_data[k_off:k_off+k_sz]
ramdisk_payload = boot_data[r_off:r_off+r_sz]

zimage_size = 10249336
zimage = kernel_payload[:zimage_size]
orig_dtb = kernel_payload[zimage_size:]

root, rsv, boot_cpuid = parse_fdt(orig_dtb)

# 1. Add qcom,msm-id and model/compat matching TWRP
msm_ids = [
    126, 8, 0x20000,
    185, 8, 0x20000,
    186, 8, 0x20000,
    126, 8, 0x20002,
    185, 8, 0x20002,
    186, 8, 0x20002
]
root.props["qcom,msm-id"] = struct.pack(f'>{len(msm_ids)}I', *msm_ids)
root.props["model"] = b"SoMC Amami ROW\x00"
root.props["compatible"] = b"somc,amami-row\x00sony,xperia-amami\x00qcom,msm8974\x00"

# 2. Fix physical memory banks avoiding the hole at 0x05d00000 - 0x0ff00000
mem_node = root.get_child("memory@0")
if not mem_node:
    mem_node = root.get_child("memory")
mem_node.props["device_type"] = b"memory\x00"

bank1_base = 0x00000000
bank1_size = 0x05d00000 # 93 MB
bank2_base = 0x0ff00000 # past 162 MB hole
bank2_size = 0x6f700000 # 1783 MB (up to 0x7f600000)

mem_reg = struct.pack('>4I', bank1_base, bank1_size, bank2_base, bank2_size)
mem_node.props["reg"] = mem_reg

# 3. Chosen node
chosen = root.get_child("chosen")
if not chosen:
    chosen = root.add_child("chosen")

KERNEL_ADDR = 0x00008000
RAMDISK_ADDR = 0x01000000
SECOND_ADDR = 0x00F00000
TAGS_ADDR = 0x01E00000
PAGE_SIZE = 2048

chosen.props["linux,initrd-start"] = struct.pack('>I', RAMDISK_ADDR)
chosen.props["linux,initrd-end"] = struct.pack('>I', RAMDISK_ADDR + len(ramdisk_payload))

bootargs = (
    "androidboot.hardware=qcom androidboot.boot_devices=soc/f9824900.mmc "
    "androidboot.selinux=permissive console=tty0 printk.devkmsg=on "
    "msm.vram=256m cma=320M msm.allow_vram_carveout=1 "
    "sysctl.kernel.panic_on_rcu_stall=1 panic=10 "
    "rcupdate.rcu_exp_cpu_stall_timeout=21000 mem_sleep_default=s2idle "
    "androidboot.debuggable=1"
)
chosen.props["bootargs"] = bootargs.encode('utf-8') + b'\x00'

# Serialize patched DTB
patched_dtb = serialize_fdt(root, rsv, boot_cpuid)
print(f"Patched DTB size: {len(patched_dtb)} bytes")

# 4. Assemble kernel payload (zImage + DTB)
new_kernel_payload = zimage + patched_dtb
new_kernel_size = len(new_kernel_payload)
print(f"New kernel payload size: {new_kernel_size} bytes")

# 5. Create Android Header v0
hdr_out = bytearray(2048)
hdr_out[:8] = b"ANDROID!"
struct.pack_into('<10I', hdr_out, 8,
    new_kernel_size, KERNEL_ADDR,
    len(ramdisk_payload), RAMDISK_ADDR,
    0, SECOND_ADDR,
    TAGS_ADDR, PAGE_SIZE, 0, 0x1200013a # os_version
)

cmd_bytes = bootargs.encode('utf-8')
hdr_out[64:64+len(cmd_bytes)] = cmd_bytes

# SHA-1
sha = hashlib.sha1()
for blob in (new_kernel_payload, ramdisk_payload, b""):
    sha.update(blob)
    sha.update(struct.pack("<I", len(blob)))
hdr_out[64+512:64+512+20] = sha.digest()

def pad(b, p):
    rem = len(b) % p
    if rem != 0: return b + (b'\x00' * (p - rem))
    return b

out_boot = bytearray()
out_boot.extend(pad(hdr_out, PAGE_SIZE))
out_boot.extend(pad(new_kernel_payload, PAGE_SIZE))
out_boot.extend(pad(ramdisk_payload, PAGE_SIZE))

out_path = r"D:\Custom Rom's Stuff\Project Custom Rom Sony Xperia Z1 Compact\boot_display_fixed.img"
with open(out_path, 'wb') as f:
    f.write(out_boot)

print(f"Successfully generated {out_path} ({len(out_boot)} bytes)!")
print(f"cmdline: {bootargs}")
