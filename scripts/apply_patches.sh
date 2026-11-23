#!/usr/bin/env bash
# Script Idempotent Apply Patches untuk Xperia Z1 Compact (amami) - Android 15 (LineageOS 22)
# Menjamin patch diaplikasikan dengan aman tanpa duplikasi.

set -e

TOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../patches" && pwd)"

echo "=== Memulai Verifikasi & Aplikasi Patch Idempotent ==="
echo "Top Source Dir: ${TOP_DIR}"
echo "Patches Dir:    ${PATCH_DIR}"

apply_patch_safe() {
    local target_repo="$1"
    local patch_file="$2"

    echo "----------------------------------------"
    echo "Target Repo: ${target_repo}"
    echo "Patch File:  $(basename "${patch_file}")"

    if [ ! -d "${TOP_DIR}/${target_repo}" ]; then
        echo "[WARNING] Direktori ${target_repo} tidak ditemukan, lewati."
        return 0
    fi

    pushd "${TOP_DIR}/${target_repo}" > /dev/null

    # Cek apakah patch sudah pernah diaplikasikan (reverse check)
    if git apply --reverse --check "${patch_file}" > /dev/null 2>&1; then
        echo "[OK] Patch sudah terpasang sebelumnya (idempotent)."
    else
        # Cek apakah patch bisa diaplikasikan bersih
        if git apply --check "${patch_file}" > /dev/null 2>&1; then
            git apply "${patch_file}"
            echo "[SUCCESS] Berhasil memasang patch."
        else
            echo "[ERROR] Gagal memasang patch! Cek konflik secara manual di ${target_repo}."
            popd > /dev/null
            return 1
        fi
    fi

    popd > /dev/null
}

# 1. Patch BPF Loader
if [ -f "${PATCH_DIR}/bpf/0001-system-bpf-bpfloader-ignore-failure-for-legacy-kernel.patch" ]; then
    apply_patch_safe "system/bpf" "${PATCH_DIR}/bpf/0001-system-bpf-bpfloader-ignore-failure-for-legacy-kernel.patch"
fi

# 2. Patch Display HWC Skia
if [ -f "${PATCH_DIR}/display/0001-hardware-qcom-display-skia-android15.patch" ]; then
    apply_patch_safe "hardware/qcom-caf/msm8974/display" "${PATCH_DIR}/display/0001-hardware-qcom-display-skia-android15.patch"
fi

# 3. Patch Build Core Artifact Path
if [ -f "${PATCH_DIR}/build/0001-relax-artifact-path-requirements.patch" ]; then
    apply_patch_safe "build/make" "${PATCH_DIR}/build/0001-relax-artifact-path-requirements.patch"
fi

echo "=========================================="
echo "Seluruh patch terverifikasi & siap dipakai."
