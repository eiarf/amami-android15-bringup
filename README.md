# Porting LineageOS 22 (Android 15) untuk Sony Xperia Z1 Compact (`amami`)

Dokumentasi teknis, analisis arsitektur BSP, local manifest, skeleton device tree, dan patch set untuk eksperimen bring-up **Android 15 (LineageOS 22.x)** pada perangkat legacy **Sony Xperia Z1 Compact (`amami` / MSM8974)**.

---

## 1. Analisis Kelayakan Teknis (Feasibility Analysis)

### Pertanyaan Kunci: Apakah Bisa?
**JAWABAN:** **BISA SECARA EKSPERIMENTAL (EXPERIMENTAL BRING-UP)**, namun **TIDAK BISA** langsung memakai manifest `115ek/manifest` secara *plug-and-play*. 

`115ek/manifest` terakhir dikembangkan untuk **LineageOS 19.0 (Android 12)**. Di Android 15 (LineageOS 22), Google dan tim LineageOS telah mengubah drastis fondasi platform:

| Komponen / Subsistem | Kondisi di `115ek/manifest` (Lineage 19 / A12) | Tantangan di LineageOS 22 (Android 15) | Solusi Rekayasa BSP |
|---|---|---|---|
| **Dukungan 32-bit CPU** | Masih didukung semi-resmi di AOSP & Lineage | LineageOS 22 menghapus pohon 32-bit resmi; AOSP mengutamakan 64-bit | Wajib setel `TARGET_ARCH := arm`, `armv7-a-neon`, `PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := relaxed` |
| **eBPF & Networking** | BPF shims sederhana via repopick `320591` | `bpfloader` Android 15 sangat ketat; kegagalan BPF menghentikan `init` & `netd` | Terapkan patch graceful warning pada `BpfLoader.cpp` agar boot tidak panik |
| **Graphics & Vulkan** | Adreno 330 OpenGL ES 3.0 via CAF display | Android 15 UI default mendorong Vulkan (SkiaVK/Turnip) | Adreno 330 tidak punya Vulkan; wajib paksa `debug.hwui.renderer=opengl` dan `SkiaGL` |
| **Display HAL (HWC)** | Memakai libskia lama | Header dan simbol Skia berubah di Android modern | Pasang patch Skia RenderEngine (Kyle Harrison patch) di HWC CAF |
| **Budget Partisi Fisik** | Muat dengan beberapa bloat | Android 15 AOSP/Lineage default melebihi 2.5 GB | Partisi `/system` amami hanya **2.43 GB**. Wajib `MALLOC_SVELTE := true` dan `debloat_lowram.xml` |

---

## 2. Pilihan Jalur Arsitektur (Architecture Paths)

### Jalur A: Downstream Kernel 3.4.113 Modernized (Jalur Rekomendasi 115ek + acroreiser)
- **Kernel:** `115ek/android_kernel_sony_msm8974` (branch `lineage-19.0-WIP`).
- **HAL:** Qualcomm CAF MSM8974 Display, Audio, Media + Proprietary blobs Sony.
- **Kelebihan:** Hardware vendor Sony (Kamera HAL1, Audio WCD9320, Modem/RIL, Wi-Fi prima) mempertahankan kompatibilitas register dan firmware asli.
- **Tantangan:** eBPF bypass di userspace dan fallback cgroups v1 (`cgroups_28.json`).
- *Status:* Telah dibuktikan bekerja pada SoC yang sama (Snapdragon 800 MSM8974) oleh developer `acroreiser` pada Nexus 5 (`hammerhead`) hingga LineageOS 22.2.

### Jalur B: Mainline Linux Kernel 6.x (`msm8974-mainline`) + Mesa Freedreno
- **Kernel:** Mainline Linux (6.6 LTS atau 6.16) + Mesa Freedreno (OpenGL ES 3.0) + DRM HWC3.
- **Kelebihan:** eBPF native, cgroups v2 native, memfd native.
- **Tantangan:** Kamera IMX220 Sony masih *half-baked* di Linux mainline, audio ALSA UCM rumit, memerlukan bootloader `lk2nd`.

---

## 3. Struktur Direktori Lokal (`D:\z1c-a15`)

```
D:\z1c-a15\
├── CHECKPOINT.md                       # Single Source of Truth & Do Not Break List
├── README.md                           # Dokumen analisis & panduan eksekusi
├── local_manifests/
│   ├── amami_lineage22.xml             # Manifest remote repository untuk repo sync
│   └── debloat_lowram.xml              # Manifest pemangkas bloatware untuk budget partisi
├── device/
│   └── sony/
│       └── amami/
│           ├── AndroidProducts.mk      # Konfigurasi lunch target
│           ├── lineage_amami.mk        # Android Go low-ram profile & device specs
│           ├── BoardConfig.mk          # 32-bit Krait, budget partisi 2.43GB, SkiaGL
│           └── device.mk               # HAL packages, properties, cgroups fallback
├── patches/
│   ├── bpf/
│   │   └── 0001-system-bpf-bpfloader-ignore-failure-for-legacy-kernel.patch
│   ├── display/
│   │   └── 0001-hardware-qcom-display-skia-android15.patch
│   └── build/
│       └── 0001-relax-artifact-path-requirements.patch
└── scripts/
    ├── apply_patches.sh                # Script verifikasi patch idempotent
    └── build_single_module.sh          # Helper kompilasi modul tunggal
```

---

## 4. Alur Eksekusi di Build Server (Setelah Konfirmasi/Approval)

Sesuai aturan **Strict Single-Module Build Policy** dan **Gerbang Konfirmasi**, perintah berikut dijalankan di build server setelah Anda memberikan persetujuan:

```bash
# 1. Inisialisasi Source Tree LineageOS 22.1 (Android 15)
mkdir -p ~/android/lineage-22 && cd ~/android/lineage-22
repo init -u https://github.com/LineageOS/android.git -b lineage-22.1 --git-lfs

# 2. Salin Local Manifests dari D:\z1c-a15\local_manifests\
mkdir -p .repo/local_manifests
cp /path/to/amami_lineage22.xml .repo/local_manifests/amami.xml
cp /path/to/debloat_lowram.xml .repo/local_manifests/debloat.xml

# 3. Sinkronisasi Source Tree (Shallow Sync untuk menghemat disk & bandwidth)
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags

# 4. Salin Device Tree & Terapkan Patch
cp -r /path/to/device/sony/amami device/sony/amami
bash /path/to/scripts/apply_patches.sh

# 5. Bring-Up Modul Tunggal (DILARANG langsung mka bacon!)
source build/envsetup.sh
lunch lineage_amami-userdebug

# Tahap A: Uji Kompilasi Kernel & Boot Image
mka bootimage

# Tahap B: Uji Kompilasi Hardware HALs Inti
mka hwcomposer.msm8974 gralloc.msm8974 audio.primary.msm8974

# Tahap C: Full ROM Build HANYA setelah uji modul tunggal di HP berhasil
# mka bacon
```

---

## 5. Ringkasan Eksekusi & Hasil Forensik Bring-Up

Detail komprehensif dari setiap iterasi bring-up, verifikasi binary, dan analisis akar masalah dicatat secara lengkap pada [CHECKPOINT.md](CHECKPOINT.md).

### Komponen Kritis yang Berhasil Diselesaikan:
1. **Appended DTB (`zImage-dtb`):**
   - Bootloader legacy Sony S1 tidak membaca tabel QCDT (`dt.img`).
   - Diaktifkan `CONFIG_ARM_APPENDED_DTB=y` dan `BOARD_KERNEL_IMAGE_NAME := zImage-dtb` dengan magic `0xd00dfeed` terverifikasi di kernel.
2. **Koreksi Ramdisk Offset (`0x01000000`):**
   - Sony S1 bootloader memuat ramdisk pada 16 MB (`0x01000000`), bukan 32 MB (`0x02000000`).
   - Disesuaikan di `BoardConfigCommon.mk` (`--ramdisk_offset 0x01000000 --tags_offset 0x01E00000`).
3. **Pembersihan Kernel Command Line Deadlock:**
   - Dihapus `earlyprintk` (yang membekukan CPU pada polling register UART tak aktif), `androidboot.first_stage_console=1`, dan `vmalloc=300M`.
4. **Syscall `renameat2` (ARM Syscall #382) & UTS Spoofing:**
   - Diimplementasikan di kernel Linux 3.4 (`arch/arm/kernel/calls.S` & `fs/namei.c`) dengan flag `RENAME_NOREPLACE` untuk kompatibilitas Android 15 `init`.
   - Spoofing versi kernel ke `4.9.337` di `include/linux/utsname.h` untuk melewati validasi versi minimal platform.
5. **Budget Partisi Fisik:**
   - `/boot`: 8,556,544 bytes (~8.16 MiB) dari batas 20 MiB (**40.80%** utilisasi).
   - `/system`: 1,594,438,152 bytes (~1.48 GiB) dari batas 2.43 GiB (**65.43%** utilisasi).
   - Flashable ROM Zip: 770,200,124 bytes (~734.52 MiB).

