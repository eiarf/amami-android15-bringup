import struct
import hashlib
import os

def pack_image():
    kernel_path = 'D:/z1c-a15/out/unpacked_fota/kernel'
    ramdisk_path = 'D:/z1c-a15/out/unpacked_boot/ramdisk.cpio.gz'
    out_path = 'D:/z1c-a15/out/boot_fota_test_signed.img'

    with open(kernel_path, 'rb') as f:
        k_data = f.read()
    with open(ramdisk_path, 'rb') as f:
        r_data = f.read()

    k_sz = len(k_data)
    r_sz = len(r_data)
    page_sz = 2048

    # Calculate SHA1 per AOSP mkbootimg update_sha
    sha = hashlib.sha1()
    sha.update(k_data)
    sha.update(struct.pack('I', k_sz))
    sha.update(r_data)
    sha.update(struct.pack('I', r_sz))
    # second is None
    sha.update(struct.pack('I', 0))
    # dt is None
    sha.update(struct.pack('I', 0))

    img_id = sha.digest().ljust(32, b'\x00')
    print('Calculated SHA1 ID:', img_id[:20].hex())

    cmdline = 'androidboot.hardware=qcom user_debug=31 msm_rtb.filter=0x37 ehci-hcd.park=3 dwc3.maximum_speed=high dwc3_msm.prop_chg_detect=Y androidboot.bootdevice=msm_sdcc.1 androidboot.selinux=permissive'
    cmdline_b = cmdline.encode('utf-8').ljust(512, b'\x00')
    extra_b = b''.ljust(1024, b'\x00')
    name = b''.ljust(16, b'\x00')

    hdr = struct.pack(
        '<8sIIIIIIIIII16s512s32s1024s',
        b'ANDROID!',
        k_sz, 0x00008000,
        r_sz, 0x01000000,
        0, 0x00f00000,
        0x01e00000, page_sz,
        0, 0x1200013a,
        name,
        cmdline_b,
        img_id,
        extra_b
    )
    hdr = hdr.ljust(page_sz, b'\x00')

    k_pad = ((k_sz + page_sz - 1) // page_sz) * page_sz - k_sz
    r_pad = ((r_sz + page_sz - 1) // page_sz) * page_sz - r_sz

    with open(out_path, 'wb') as f:
        f.write(hdr)
        f.write(k_data)
        f.write(b'\x00' * k_pad)
        f.write(r_data)
        f.write(b'\x00' * r_pad)

    size = os.path.getsize(out_path)
    with open(out_path, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    print(f'Packed {out_path}: {size:,} bytes | SHA-256: {sha256}')

if __name__ == '__main__':
    pack_image()
