#!/usr/bin/env bash
# Partition budget, S1Boot header, DTB, and SHA-256 verification gate for amami
set -euo pipefail

OUT_DIR="${1:-${OUT:-out/target/product/amami}}"

BOOT_LIMIT=20971520
REC_LIMIT=20971520
SYS_LIMIT=2436890624
SYS_MARGIN=52428800  # 50 MiB safety margin

echo "=== Verifying amami build outputs in: ${OUT_DIR} ==="

check_size() {
    local file="$1"
    local limit="$2"
    local label="$3"
    if [ ! -f "${file}" ]; then
        echo "[SKIP] ${label}: ${file} not built yet."
        return 0
    fi
    local sz
    sz=$(stat -c%s "${file}")
    if [ "${sz}" -gt "${limit}" ]; then
        echo "[FAIL] ${label}: ${sz} bytes EXCEEDS limit ${limit} bytes!"
        return 1
    fi
    echo "[PASS] ${label}: ${sz} / ${limit} bytes ($((sz * 100 / limit))%)"
}

check_size "${OUT_DIR}/boot.img" "${BOOT_LIMIT}" "boot.img"
check_size "${OUT_DIR}/recovery.img" "${REC_LIMIT}" "recovery.img"
check_size "${OUT_DIR}/system.img" "$((SYS_LIMIT - SYS_MARGIN))" "system.img (with 50 MiB margin)"

if [ -f "${OUT_DIR}/boot.img" ]; then
    python3 - "${OUT_DIR}/boot.img" << 'PYEOF'
import struct, sys
p = sys.argv[1]
with open(p, 'rb') as f:
    hdr = f.read(2048)
    f.seek(0)
    raw = f.read()
magic, k_sz, k_addr, r_sz, r_addr, s_sz, s_addr, tags_addr, page_sz, dt_sz = struct.unpack('<8sIIIIIIIII', hdr[:44])
print(f"boot.img header: magic={magic} k_addr={hex(k_addr)} r_addr={hex(r_addr)} tags_addr={hex(tags_addr)} page_sz={page_sz} dt_sz={dt_sz}")
assert magic == b'ANDROID!', "Invalid boot magic"
assert k_addr == 0x00008000, f"Unexpected kernel_addr: {hex(k_addr)}"
assert r_addr == 0x01000000, f"Unexpected ramdisk_addr (S1Boot requires 0x01000000): {hex(r_addr)}"
assert tags_addr == 0x01e00000, f"Unexpected tags_addr: {hex(tags_addr)}"
assert dt_sz == 0, f"dt_sz must be 0 (appended DTB required for S1Boot), got {dt_sz}"
k_end = page_sz + k_sz
k_blob = raw[page_sz:k_end]
assert b'\xd0\x0d\xfe\xed' in k_blob, "Appended DTB magic (0xd00dfeed) not found in kernel payload!"
print("[PASS] S1Boot header & appended DTB magic verified.")
PYEOF
fi

echo "=== SHA-256 Checksums ==="
for f in "${OUT_DIR}/boot.img" "${OUT_DIR}/recovery.img" "${OUT_DIR}"/lineage-20.0-*-amami.zip; do
    if [ -f "$f" ]; then
        sha256sum "$f"
    fi
done
