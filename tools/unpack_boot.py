import os, struct

p = r"D:\Custom Rom's Stuff\Project Custom Rom Sony Xperia Z1 Compact"
boot_path = os.path.join(p, "boot.img")

with open(boot_path, 'rb') as f:
    hdr = f.read(2048)
    magic, k_sz, k_addr, r_sz, r_addr, s_sz, s_addr, t_addr, page_sz = struct.unpack('<8s8I', hdr[:40])
    
    # Kernel starts at page_sz
    f.seek(page_sz)
    k_data = f.read(k_sz)
    
    # Ramdisk starts at page_sz + ceil(k_sz / page_sz) * page_sz
    k_pages = (k_sz + page_sz - 1) // page_sz
    r_offset = page_sz + k_pages * page_sz
    f.seek(r_offset)
    r_data = f.read(r_sz)

print(f"Kernel data length: {len(k_data)}")
print(f"Ramdisk data length: {len(r_data)}")

# Search for DTB magic 0xd00dfeed inside k_data!
dtb_magic = b'\xd0\x0d\xfe\xed'
dtb_offset = k_data.find(dtb_magic)
print(f"DTB magic offset in kernel: {dtb_offset}")

if dtb_offset != -1:
    dtb_header = k_data[dtb_offset : dtb_offset + 40]
    total_size = struct.unpack('>I', dtb_header[4:8])[0]
    print(f"DTB total size: {total_size} bytes")
    # Read root compatible string
    # Let's inspect DTB string block
    strings_offset = struct.unpack('>I', dtb_header[12:16])[0]
    struct_offset = struct.unpack('>I', dtb_header[8:12])[0]
    print(f"DTB struct_offset: {struct_offset}, strings_offset: {strings_offset}")
