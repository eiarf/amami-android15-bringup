#!/usr/bin/env bash
# Idempotent patch applier for Xperia Z1 Compact (amami) - Android 13 (LineageOS-UL 20.0)
set -euo pipefail

TOP_DIR="${1:-$(pwd)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_ROOT="$(cd "${SCRIPT_DIR}/../patches" && pwd)"

echo "=== Applying z1c-a13 idempotent patches ==="
echo "Source tree: ${TOP_DIR}"
echo "Patch root:  ${PATCH_ROOT}"

apply_one() {
    local rel_repo="$1"
    local patch_file="$2"
    local repo_dir="${TOP_DIR}/${rel_repo}"

    echo "----------------------------------------"
    echo "Repo:  ${rel_repo}"
    echo "Patch: $(basename "${patch_file}")"

    if [ ! -d "${repo_dir}" ]; then
        echo "[ERROR] Directory ${repo_dir} not found!"
        return 1
    fi

    pushd "${repo_dir}" > /dev/null
    if git apply --reverse --check "${patch_file}" > /dev/null 2>&1; then
        echo "[OK] Already applied (idempotent)."
    elif git apply --check "${patch_file}" > /dev/null 2>&1; then
        git apply "${patch_file}"
        echo "[APPLIED] Patch applied cleanly."
    else
        echo "[ERROR] Patch conflict in ${rel_repo}!"
        popd > /dev/null
        return 1
    fi
    popd > /dev/null
}

apply_one "build/soong" "${PATCH_ROOT}/build_soong/0001-soong-build-fixes.patch"
apply_one "device/sony/amami" "${PATCH_ROOT}/device_sony_amami/0001-amami-adapt-for-lineage-20.0.patch"
apply_one "device/sony/msm8974-common" "${PATCH_ROOT}/device_sony_msm8974-common/0001-msm8974-common-all-fixes.patch"
apply_one "device/sony/rhine-common" "${PATCH_ROOT}/device_sony_rhine-common/0001-rhine-common-amami-a13-fixes.patch"
apply_one "kernel/sony/msm8974" "${PATCH_ROOT}/kernel_sony_msm8974/0001-amami-a13-cgroups-dtb-debug-and-vmpressure.patch"
apply_one "packages/apps/Settings" "${PATCH_ROOT}/packages_apps_Settings/0001-Settings-lineage-ul-compat-fixes.patch"
apply_one "packages/apps/Trebuchet" "${PATCH_ROOT}/packages_apps_Trebuchet/0001-Trebuchet-lineage-ul-compat-fixes.patch"
apply_one "packages/modules/Bluetooth" "${PATCH_ROOT}/packages_modules_Bluetooth/0001-btu_task-do-not-fatal-on-rt-scheduling-failure.patch"
apply_one "packages/providers/ContactsProvider" "${PATCH_ROOT}/packages_providers_ContactsProvider/0001-SelectionBuilder-avoid-null-consumer-NPE.patch"
apply_one "packages/services/Mms" "${PATCH_ROOT}/packages_services_Mms/0001-MmsService-lineage-ul-aidl-compat.patch"
apply_one "packages/services/Telephony" "${PATCH_ROOT}/packages_services_Telephony/0001-Telephony-lineage-ul-compat-fixes.patch"
apply_one "system/tools/aidl" "${PATCH_ROOT}/system_tools_aidl/0001-aidl-compat-fixes.patch"

echo "========================================"
echo "All 12 patches verified and applied."
