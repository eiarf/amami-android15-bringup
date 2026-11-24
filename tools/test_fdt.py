import struct
from collections import OrderedDict

FDT_MAGIC = 0xd00dfeed
FDT_BEGIN_NODE = 1
FDT_END_NODE = 2
FDT_PROP = 3
FDT_NOP = 4
FDT_END = 9

class FDTNode:
    def __init__(self, name):
        self.name = name
        self.props = OrderedDict()
        self.children = []

    def get_child(self, name):
        for c in self.children:
            if c.name == name:
                return c
        return None

    def add_child(self, name):
        c = FDTNode(name)
        self.children.append(c)
        return c

def parse_fdt(blob):
    hdr = blob[:40]
    magic, totalsize, off_dt_struct, off_dt_strings, off_mem_rsvmap, version, last_comp_version, boot_cpuid_phys, size_dt_strings, size_dt_struct = struct.unpack('>10I', hdr)
    assert magic == FDT_MAGIC, f"Invalid magic: {hex(magic)}"
    
    # Read reservations
    rsv = []
    r_off = off_mem_rsvmap
    while r_off < off_dt_struct:
        addr, size = struct.unpack('>2Q', blob[r_off:r_off+16])
        r_off += 16
        if addr == 0 and size == 0:
            break
        rsv.append((addr, size))
    
    strings = blob[off_dt_strings:off_dt_strings+size_dt_strings]
    def get_str(o):
        end = strings.find(b'\x00', o)
        return strings[o:end].decode('utf-8', errors='ignore')

    pos = off_dt_struct
    end_pos = off_dt_struct + size_dt_struct
    root = None
    stack = []

    while pos < end_pos:
        tag = struct.unpack('>I', blob[pos:pos+4])[0]
        pos += 4
        if tag == FDT_BEGIN_NODE:
            name_end = blob.find(b'\x00', pos)
            node_name = blob[pos:name_end].decode('utf-8', errors='ignore')
            pos = (name_end + 1 + 3) & ~3
            node = FDTNode(node_name)
            if not root:
                root = node
            else:
                stack[-1].children.append(node)
            stack.append(node)
        elif tag == FDT_END_NODE:
            stack.pop()
        elif tag == FDT_PROP:
            prop_len, name_off = struct.unpack('>2I', blob[pos:pos+8])
            pos += 8
            data = blob[pos:pos+prop_len]
            pos = (pos + prop_len + 3) & ~3
            name = get_str(name_off)
            stack[-1].props[name] = data
        elif tag == FDT_NOP:
            pass
        elif tag == FDT_END:
            break

    return root, rsv, boot_cpuid_phys

def serialize_fdt(root, rsv=[], boot_cpuid_phys=0):
    # Collect all strings
    strings = bytearray()
    string_map = {}

    def get_name_offset(name):
        if name in string_map:
            return string_map[name]
        off = len(strings)
        strings.extend(name.encode('utf-8') + b'\x00')
        string_map[name] = off
        return off

    # Build dt_struct
    struct_bytes = bytearray()

    def serialize_node(node):
        struct_bytes.extend(struct.pack('>I', FDT_BEGIN_NODE))
        name_bytes = node.name.encode('utf-8') + b'\x00'
        # align to 4
        rem = len(name_bytes) % 4
        if rem != 0:
            name_bytes += b'\x00' * (4 - rem)
        struct_bytes.extend(name_bytes)

        for prop_name, prop_data in node.props.items():
            name_off = get_name_offset(prop_name)
            struct_bytes.extend(struct.pack('>3I', FDT_PROP, len(prop_data), name_off))
            rem = len(prop_data) % 4
            pad = b'\x00' * ((4 - rem) if rem != 0 else 0)
            struct_bytes.extend(prop_data + pad)

        for child in node.children:
            serialize_node(child)

        struct_bytes.extend(struct.pack('>I', FDT_END_NODE))

    serialize_node(root)
    struct_bytes.extend(struct.pack('>I', FDT_END))

    # Calculate offsets
    # Header: 40 bytes
    # Align to 8 bytes for mem_rsvmap
    off_mem_rsvmap = 40
    # Reserve map: 16 bytes per entry, terminated by 16 zero bytes
    rsv_bytes = bytearray()
    for addr, sz in rsv:
        rsv_bytes.extend(struct.pack('>2Q', addr, sz))
    rsv_bytes.extend(struct.pack('>2Q', 0, 0))

    off_dt_struct = off_mem_rsvmap + len(rsv_bytes)
    # Align struct offset
    rem = off_dt_struct % 8
    if rem != 0:
        off_dt_struct += (8 - rem)

    size_dt_struct = len(struct_bytes)
    off_dt_strings = off_dt_struct + size_dt_struct
    size_dt_strings = len(strings)

    totalsize = off_dt_strings + size_dt_strings
    # Pad totalsize to 8 bytes
    rem = totalsize % 8
    if rem != 0:
        totalsize += (8 - rem)

    header = struct.pack('>10I',
        FDT_MAGIC,
        totalsize,
        off_dt_struct,
        off_dt_strings,
        off_mem_rsvmap,
        17, # version
        16, # last_comp_version
        boot_cpuid_phys,
        size_dt_strings,
        size_dt_struct
    )

    blob = bytearray(totalsize)
    blob[0:len(header)] = header
    blob[off_mem_rsvmap:off_mem_rsvmap+len(rsv_bytes)] = rsv_bytes
    blob[off_dt_struct:off_dt_struct+len(struct_bytes)] = struct_bytes
    blob[off_dt_strings:off_dt_strings+len(strings)] = strings

    return bytes(blob)

# Let's test on original DTB
boot_path = r"D:\Custom Rom's Stuff\Project Custom Rom Sony Xperia Z1 Compact\boot.img"
dtb_offset = 2048 + 10249336
with open(boot_path, 'rb') as f:
    f.seek(dtb_offset)
    dtb_data = f.read(49790)

root, rsv, boot_cpuid = parse_fdt(dtb_data)
print(f"Parsed root: '{root.name}', children: {len(root.children)}, props: {len(root.props)}")
rebuilt = serialize_fdt(root, rsv, boot_cpuid)
print(f"Original DTB size: {len(dtb_data)}, Rebuilt DTB size: {len(rebuilt)}")

# Parse rebuilt to verify validity
root2, rsv2, boot_cpuid2 = parse_fdt(rebuilt)
print(f"Re-parsed root: '{root2.name}', children: {len(root2.children)}, props: {len(root2.props)}")
print("Verification: SUCCESS!")
