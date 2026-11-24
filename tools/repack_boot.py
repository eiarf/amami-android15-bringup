import struct, os

p = r"D:\Custom Rom's Stuff\Project Custom Rom Sony Xperia Z1 Compact"
src_boot = os.path.join(p, "boot.img")
dst_boot = os.path.join(p, "boot_test.img")

with open(src_boot, 'rb') as f:
    hdr_data = f.read(2048)
    magic, k_sz, k_addr, r_sz, r_addr, s_sz, s_addr, t_addr, page_sz, unused, os_ver, bname, cmdline = struct.unpack('<8s10I16s512s', hdr_data[:576])
    
    # Read kernel and ramdisk
    k_pages = (k_sz + page_sz - 1) // page_sz
    r_pages = (r_sz + page_sz - 1) // page_sz
    
    f.seek(page_sz)
    k_data = f.read(k_sz)
    
    f.seek(page_sz + k_pages * page_sz)
    r_data = f.read(r_sz)

new_cmdline = b"androidboot.hardware=qcom androidboot.boot_devices=soc/f9824900.mmc androidboot.selinux=permissive"
new_cmdline = new_cmdline.ljust(512, b'\x00')

new_hdr = struct.pack('<8s10I16s512s', magic, k_sz, k_addr, r_sz, r_addr, s_sz, s_addr, t_addr, page_sz, unused, os_ver, bname, new_cmdline)
new_hdr = new_hdr.ljust(page_sz, b'\x00')

with open(dst_boot, 'wb') as f:
    f.write(new_hdr)
    # Write kernel padded
    f.write(k_data)
    f.write(b'\x00' * (k_pages * page_sz - len(k_data)))
    # Write ramdisk padded
    f.write(r_data)
    f.write(b'\x00' * (r_pages * page_sz - len(r_data)))

print(f"Created {dst_boot} ({os.path.getsize(dst_boot)} bytes)")
print("New cmdline:", new_cmdline.split(b'\x00')[0].decode('latin1'))
