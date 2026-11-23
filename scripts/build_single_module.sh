#!/usr/bin/env bash
# Script Helper Kompilasi Modul Tunggal (Strict Single-Module Policy)
# Memastikan tidak ada full build dijalankan sebelum boot & subsistem dasar terbukti stabil.

set -e

TOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${TOP_DIR}"

if [ -z "$1" ]; then
    echo "Penggunaan: ./scripts/build_single_module.sh <target>"
    echo "Contoh target:"
    echo "  bootimage            - Kompilasi boot.img (Kernel + Ramdisk)"
    echo "  hwcomposer.msm8974   - Kompilasi modul HAL Display"
    echo "  gralloc.msm8974      - Kompilasi modul HAL Gralloc"
    echo "  audio.primary.msm8974- Kompilasi modul HAL Audio"
    echo "  systemimage          - Kompilasi system.img (setelah single modules lolos)"
    exit 1
fi

TARGET="$1"

echo "=== Menyiapkan Environment Build ==="
source build/envsetup.sh
lunch lineage_amami-userdebug

echo "=== Memulai Kompilasi Modul Tunggal: ${TARGET} ==="
mka "${TARGET}"

echo "=== Selesai: Modul ${TARGET} berhasil dibangun! ==="
