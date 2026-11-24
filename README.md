# Android 13 (LineageOS-UL 20.0) — Sony Xperia Z1 Compact (`amami`)

Workspace persiapan lokal (`D:\z1c-a13`) untuk membangun Custom ROM **Android 13 (`lineage-20.0`)** di Sony Xperia Z1 Compact (`amami` / MSM8974 / 32-bit Krait ARMv7), disusun mengikuti `guideline.md` (*Evidence-First*, *Single-Module Build Policy*, *Sync-Before-Build Gate*, dan *Partition Budget Audit*).

---

## 1. Hasil Analisis 3 Referensi Utama

| Referensi | Hasil Audit Kode Sumber | Keputusan Arsitektur |
|---|---|---|
| **`https://github.com/115ek/manifest`** | Basis `amami` terakhir berhenti di `lineage-19.0-WIP` (`amami_lineage_19.0.xml`), mengambil `device/sony/amami` dari `lin18-microG` (`lineage-18.1`) dan vendor blob dari `lin18-microG/proprietary_vendor_sony_amami`. | `lin18-microG/android_device_sony_amami` & `proprietary_vendor_sony_amami` tetap dipakai, lalu dipatch untuk `lineage-20.0`, sementara `rhine-common` & `msm8974-common` dinaikkan ke `sony-togari-dev@lineage-20.0` (keluarga Rhine yang sama, sudah memiliki Audio HAL v6.0, BT Audio v2.1, RIL AOSP 12+, `ro.kernel.ebpf.supported=false`, dan `threaded` GLES). |
| **`https://github.com/lineageos`** | `LineageOS/android` (`lineage-20.0`) sudah menghapus `msm8974` CAF HAL (`display/audio/media` mentok di `lineage-18.1`), menghapus `sepolicy` legacy, mewajibkan eBPF >= 4.9, menghapus legacy FunctionFS `adbd`, dan mewajibkan `cgroup2`. | Gunakan **`LineageOS-UL/android` (`lineage-20.0`)** (fork resmi Ultra-Legacy berbasis `LineageOS` `lineage-20.0` dengan ~32 repo kompatibilitas Linux 3.4: no-eBPF `system/bpf` & `netd` & `Connectivity`, legacy FunctionFS `adb` via `ro.adb.nonblocking_ffs=0`, Camera HALv1, non-cgroupv2 `system/core`, `msm8974` CAF HAL `lineage-20.0`, dan `GLESRenderEngine` `threaded` yang menghindari bug Adreno 330 SkiaGL Android 15). |
| **`https://gitlab.com/MakeDecisionWorth/android_kernel_sony_msm8974`** | Branch `lineage-20.0` aktif dan memiliki patch Android 13 penting (`aa10daf4` cgroup configs, ChaCha20 CRNG, `hwrng`, `binder` & `lmk` 3.18), **tetapi hanya berisi perangkat Shinano (Z2/Z3/Z3C)** — tidak ada defconfig maupun DTS `rhine`/`amami`. | Gunakan **`sony-togari-dev/android_kernel_sony_msm8974@lineage-20.0`** yang sudah membawa seluruh DTS/driver `rhine`/`amami` + backport ChaCha20/binder/lmk/`fget_raw_light` yang setara, lalu porting konfigurasi cgroup Android 13 MakeDecisionWorth (`aa10daf4`) + perbaikan `amami` dari `D:\z1c-a15` (`zImage-dtb`, `mm/vmpressure.c`, `CONFIG_IKCONFIG_PROC=y`, `CONFIG_SLUB_DEBUG=y`, `scripts/xz_wrap.sh`). |

---

## 2. Struktur File (`D:\z1c-a13`)

```text
D:\z1c-a13\
├── CHECKPOINT.md
├── README.md
├── local_manifests/
│   ├── amami.xml                       # Local manifest untuk LineageOS-UL 20.0
│   └── debloat_lowram.xml.optional     # Opsional jika /system butuh margin lebih
├── patches/
│   ├── device_sony_amami/
│   │   └── 0001-amami-adapt-for-lineage-20.0.patch
│   ├── device_sony_rhine-common/
│   │   └── 0001-rhine-common-amami-a13-fixes.patch
│   ├── device_sony_msm8974-common/
│   │   └── 0001-msm8974-common-gps-format-fixes.patch
│   └── kernel_sony_msm8974/
│       └── 0001-amami-a13-cgroups-dtb-debug-and-vmpressure.patch
└── scripts/
    ├── apply_patches.sh                # Idempotent patch applier (git apply)
    └── verify_build_output.sh          # Cek batas partisi, header S1Boot, DTB magic, SHA-256
```

---

## 3. Batas Partisi Fisik (`mmcblk0`)

- `boot` (`mmcblk0p14`): `<= 20,971,520` bytes (20 MiB) — `zImage-dtb` + `ramdisk_offset=0x01000000`, `tags_offset=0x01E00000`, `dt_sz=0`
- `recovery` (`FOTAKernel`, `mmcblk0p16`): `<= 20,971,520` bytes (20 MiB)
- `system` (`mmcblk0p23`): `<= 2,436,890,624` bytes (target raw <= `2,384,461,824` bytes, sisakan margin ~50–60 MiB ext4)
- `cache`: `209,715,200` bytes | `userdata`: `12,891,175,936` bytes

---

## 4. Rencana Eksekusi Server (HANYA Setelah User Approve)

Mengikuti **Strict Single-Module Build Policy** (`guideline.md` Bagian A.3 & Bagian B):

### Tahap A — Sync & Patch Tree (Fase 1)
```bash
mkdir -p ~/android/lineage-ul-20 && cd ~/android/lineage-ul-20
repo init -u https://github.com/LineageOS-UL/android.git -b lineage-20.0 --git-lfs
mkdir -p .repo/local_manifests
cp /path/to/z1c-a13/local_manifests/amami.xml .repo/local_manifests/amami.xml
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags

# Terapkan patch idempotent
bash /path/to/z1c-a13/scripts/apply_patches.sh "$(pwd)"
```

### Tahap B — First Boot Bring-Up (`mka bootimage` terlebih dahulu, DILARANG `mka bacon`)
```bash
source build/envsetup.sh
export WITH_ADB_INSECURE=true   # Hanya untuk fase bring-up (Phase 1-3)
lunch lineage_amami-userdebug

# 1. Kompilasi modul bootimage saja untuk verifikasi kernel + appended DTB + ramdisk
mka bootimage
bash /path/to/z1c-a13/scripts/verify_build_output.sh "$OUT"
```
> Catatan: Jangan menjalankan `mka bacon` / `brunch amami` sebelum `boot.img`, `system.img` awal / HAL tunggal teruji di perangkat dan `CHECKPOINT.md` diperbarui per subsistem (Display/Touch/ADB → Audio/Jack → Camera/Media → RIL/Wi-Fi/BT/GNSS → Audit Idle & Stress → Clean Packaging).
