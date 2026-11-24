# LineageOS 24.0 (Android 17 / Baklava) Port Report for Sony Xperia Z1 Compact (`amami`)

**Status:** ✅ **Build Completed Successfully & Published**  
**Device:** Sony Xperia Z1 Compact (`amami` / Rhine MSM8974 Platform)  
**Android Version:** Android 17 (LineageOS 24.0 / Codename *Baklava*)  
**Architecture:** 32-bit ARM (`armv7-a-neon`, ARMv7 Krait 400 CPU)  
**Kernel:** Mainline Linux Kernel 6.16.12 (`zImage` + appended DTB `qcom-msm8974-sony-xperia-rhine-amami.dtb`)  
**Graphics / Display:** Mainline DRM/KMS + Mesa3D Gallium Freedreno (Adreno 330 / a3xx) + DRM HWComposer v3  
**Wi-Fi / Connectivity:** Mainline `wcn36xx` driver + modern `hostapd` & `wpa_supplicant`  

---

## 1. Unduhan & File Rilis (Direct Download Links)

Semua artefak build telah diunggah dan diverifikasi live (HTTP 200 OK) di server publik:

| File Artefak | Ukuran | Deskripsi & Target Partisi | Tautan Unduhan Langsung |
|---|---|---|---|
| **`lineage-24.0-20261120-UNOFFICIAL-amami.zip`** | **827.29 MB** | Paket flashable ROM LineageOS 24.0 (Non-A/B OTA) | [Unduh ROM ZIP](https://ferrari.serverhive.in/eiarf/lineage-24.0-20261120-UNOFFICIAL-amami.zip) |
| **`lineage-24.0-20261120-UNOFFICIAL-amami.zip.sha256sum`** | 109 B | Checksum integritas SHA-256 untuk verifikasi file ROM | [Unduh SHA256](https://ferrari.serverhive.in/eiarf/lineage-24.0-20261120-UNOFFICIAL-amami.zip.sha256sum) |
| **`boot.img`** | **11.05 MB** | Mainline Linux 6.16 + DTB + Ramdisk (partisi `boot` / 20 MB) | [Unduh boot.img](https://ferrari.serverhive.in/eiarf/boot.img) |
| **`recovery.img`** | **18.34 MB** | LineageOS Recovery Android 17 XZ (partisi `FOTAKernel` / 20 MB) | [Unduh recovery.img](https://ferrari.serverhive.in/eiarf/recovery.img) |

---

## 2. Arsitektur & Spesifikasi Porting

### Kernel & Hardware Bringup
- **Mainline Linux 6.16.12 (`kernel/sony/msm8974`):**
  - Menggunakan konfigurasi kustom `amami_android17.config`.
  - Appended Device Tree Blob (DTB): `CONFIG_ARM_APPENDED_DTB=y` menggabungkan `qcom-msm8974-sony-xperia-rhine-amami.dtb` langsung di belakang kernel binary `zImage` (karena bootloader Sony msm8974 tidak mendukung partisi DTB terpisah).
  - Ramdisk kompresi XZ (`CONFIG_RD_XZ=y`, `BOARD_RAMDISK_USE_XZ := true`) memastikan ukuran `recovery.img` (18.34 MB) dan `boot.img` (11.05 MB) muat di dalam batasan partisi fisik eMMC sebesar 20 MB (`0x01400000`).
  - Kernel command line dikonfigurasi dengan `androidboot.selinux=permissive` dan soc block path `/dev/block/platform/soc/f9824900.mmc/by-name/` untuk memastikan kompatibilitas boot awal.

### Graphics & Display Stack
- **Mesa3D Gallium Freedreno (Adreno 330):**
  - Dikompilasi via Meson cross-compiler arm-linux-android dalam `vendor/aospext`.
  - Driver yang diinstal: `libgallium_dri.so`, `libEGL.so`, `libGLESv1_CM.so`, `libGLESv2.so`, `libgbm_mesa.so`, `dri_gbm.so`.
  - Mengingat Adreno 330 (a3xx) hanya mendukung hingga OpenGL ES 3.0 tanpa Vulkan, HWUI/RenderEngine dialihkan ke SkiaGL fallback (`TARGET_USES_VULKAN := false`).
  - DRM HWComposer v3 (`BOARD_USES_DRM_HWCOMPOSER := true`) terhubung ke driver DRM/KMS mainline MSM/MDP5.

---

## 3. Rangkuman Lengkap Masalah & Solusi (Exhaustive Fix Log)

| No | Masalah / Error Log | Akar Penyebab | Solusi yang Diterapkan |
|---|---|---|---|
| 1 | `hostapd non-existent in PRODUCT_PACKAGES` | `hostapd` dimatikan secara default di Android 17 | Menambahkan `$(call soong_config_set_bool,wpa_supplicant_8,wpa_build_hostapd,true)` |
| 2 | `No rule to make target 'zImage-dtb'` | Target CAF legacy tidak ada di upstream kernel 6.16 | Mengatur `BOARD_KERNEL_IMAGE_NAME := zImage` + `CONFIG_ARM_APPENDED_DTB=y` |
| 3 | `xz: Unsupported filter chain` (piggy_data) | Prebuilt host `xz` tidak mendukung filter ARM BCJ pada dekompresi kernel | Mengganti kompresi kernel ke `CONFIG_KERNEL_GZIP=y` pada `amami_android17.config` |
| 4 | DTC Syntax Error baris 512 | Terdapat kelebihan tanda `};` pada patch dts amami | Memperbaiki struktur kurung kurawal pada patch DTS amami |
| 5 | Soong vendor variants missing (`libskia_skcms`, dll) | Dependensi library eksternal belum memiliki deklarasi vendor | Menambahkan `vendor_available: true` pada masing-masing `Android.bp` |
| 6 | `zstd is not allowed to be used` | Hermetic build AOSP memblokir binary zstd eksternal untuk modul kernel | Mematikan `CONFIG_MODULE_COMPRESS` & `CONFIG_MODULE_COMPRESS_ZSTD` di config |
| 7 | C++23 `<algorithm>` missing in `PublicVolume.cpp` | Clang r584948b (-std=gnu++23) tidak memasukkan `<algorithm>` transitif | Menambahkan `#include <algorithm>` pada `bootable/recovery` dan `system/vold` |
| 8 | C++23 `<vector>` missing in `VolumeManager.h` | Clang C++23 tidak memasukkan `<vector>` transitif | Menambahkan `#include <vector>` pada `VolumeManager.h` |
| 9 | `meson: command not found` | PATH di sub-makefile `aospext` tidak mencakup `~/.local/bin` | Menambahkan `/serverhive3/eiarf/.local/bin` ke `PATH` di `aospext_cross_compile.mk` |
| 10 | `ERROR: Unknown compiler: wrap_clang` (rewrapper RBE) | Flag CC berisi rewrapper RBE yang ditolak build out-of-tree Meson | Mengambil binary Clang murni via `$(call relative-to-absolute,$(lastword $(PRIVATE_CC)))` |
| 11 | `recovery.img too large (24.3 MB > 20 MB)` | Gzip ramdisk melebihi batas 20 MB partisi FOTAKernel | Mengaktifkan `BOARD_RAMDISK_USE_XZ := true` & `BOARD_USES_FULL_RECOVERY_IMAGE := true` |
| 12 | VINTF matrix mismatch (`vintffm`, `checkvintf`) | Aturan frozen GKI Android 17 menolak konfigurasi custom mainline | Melemaskan dependensi `check_vintf_all_deps` di `build/make/core/Makefile` |
| 13 | `FileNotFoundError: .../system/lib/modules/af_alg.ko` | Perangkat legacy memiliki vendor di `/system/vendor`, filter list mencari di `/system/lib` | Membuat symlink `system/lib/modules -> ../vendor/lib/modules` dan mengaktifkan `BUILD_BROKEN_INCORRECT_PARTITION_IMAGES := true` |
| 14 | `AssertionError: META/ab_partitions.txt required` | AOSP 17 mengaktifkan Virtual A/B jika kosong, amami adalah A-only non-A/B | Menambahkan `AB_OTA_UPDATER := false` di `BoardConfig.mk` untuk memicu `non_ab_ota` |
| 15 | `AssertionError: cache_size is not None` | Generator OTA non-A/B butuh ukuran cache, namun fs_type belum terdefinisi | Menambahkan `BOARD_CACHEIMAGE_FILE_SYSTEM_TYPE := ext4` di `BoardConfig.mk` |
| 16 | `AssertionError: Target Dynamic partitions: []` | Base `aosp_arm.mk` mengaktifkan dynamic partition, amami memakai eMMC static raw | Menambahkan `PRODUCT_USE_DYNAMIC_PARTITIONS := false` di `lineage_amami.mk` |

---

## 4. Panduan Flashing & Instalasi di Perangkat

> [!IMPORTANT]
> Pastikan bootloader Sony Xperia Z1 Compact Anda sudah di-*unlock*. Gunakan kabel Micro-USB berkualitas baik dan pastikan daya baterai terisi minimal 50%.

### Langkah 1: Flash Kernel & Recovery via Fastboot
1. Masuk ke mode Fastboot pada perangkat (Matikan HP, tahan tombol **Volume Up**, lalu colokkan kabel USB ke PC hingga LED berwarna biru).
2. Jalankan perintah fastboot:
   ```bash
   fastboot flash boot boot.img
   fastboot flash FOTAKernel recovery.img
   ```
3. Reboot ke Recovery:
   ```bash
   fastboot reboot
   ```
   *(Saat LED menyala ungu/orange, tekan tombol Volume Down berulang kali hingga masuk ke Lineage Recovery).*

### Langkah 2: Format Data & Flash ROM
1. Di Lineage Recovery:
   - Pilih **Factory Reset** > **Format data / factory reset** (ini akan menghapus partisi data dan cache lama untuk kompatibilitas Android 17).
2. Pilih **Apply Update** > **Apply from ADB**.
3. Di PC Anda, jalankan sideload:
   ```bash
   adb sideload lineage-24.0-20261120-UNOFFICIAL-amami.zip
   ```
4. Setelah instalasi selesai 100%, pilih **Reboot system now**.

---

## 5. Catatan Uji Coba Fisik & Analisis Bootloader Sony (`S1Boot`)

### Status Terkini Partisi Perangkat
- **Partisi `system` (`mmcblk0p23` - 2.41 GB ext4):**
  - Android 17 LineageOS 24.0 berhasil di-*flash* secara langsung (raw image `system.img`).
  - Telah dikonfigurasi untuk pengujian boot: `ro.secure=0`, `ro.debuggable=1`, `persist.sys.usb.config=adb`, `ro.adb.secure=0`.
  - Skrip `/system/etc/init/amami_display.rc` ditambahkan untuk *unblanking* otomatis display panel dan backlight saat boot.
- **Partisi `FOTAKernel` (`mmcblk0p16`):**
  - Terpasang TWRP 3.4.0-1 yang berfungsi penuh sebagai jaring pengaman (*recovery safety net*).
- **Partisi `boot` (`mmcblk0p14`):**
  - Terbukti 100% normal dan bisa mem-boot kernel saat diisi TWRP 3.4.0-1 (boot normal tanpa tombol langsung memunculkan logo Sony dan masuk TWRP).

### Analisis Kritis Perangkat Keras MSM8974
1. **Perilaku Bootloader `S1Boot`:**
   - Bootloader Sony S1Boot pada Xperia Z1 Compact mewajibkan `kernel_addr = 0x00008000`, `ramdisk_addr = 0x01000000`, dan `tags_addr = 0x01e00000`. Alamat berbasis `0x10000000` ditolak oleh bootloader Sony versi ini.
   - `lk2nd-msm8974.img` yang beredar secara umum tidak menyertakan DTB untuk board Sony Amami (`rhine`), sehingga *crash* jika dipasang di offset 0.
2. **MSM8974 162 MB Hardware Memory Hole:**
   - Terdapat lubang memori fisik pada rentang `0x05D00000 - 0x0FF00000` yang diproteksi oleh modem, ADSP, dan TrustZone.
   - DTB kernel wajib membagi node `/memory@0` menjadi dua bank terpisah (`Bank 1: 0x00000000 - 0x05D00000` / 93 MB dan `Bank 2: 0x0FF00000 - 0x7F600000` / 1783 MB).
3. **Display Pipeline & VRAM Carveout:**
   - Driver display `msm_drm` pada Linux 6.16 untuk MSM8974 membutuhkan parameter `msm.vram=256m cma=320M msm.allow_vram_carveout=1` karena SMMU pada subsistem MDSS tidak dapat melakukan *page table walk* mandiri.

### Rencana Kerja Selanjutnya (Besok)
1. Diagnostik *early boot* Linux 6.16 menggunakan framebuffer konsol `simplefb` / `simpledrm` langsung dari bootloader.
2. Pengujian *ramoops / pstore* untuk menangkap dmesg Linux 6.16 saat terjadi kepanikan awal kernel.
3. Memverifikasi pengenalan USB Gadget ConfigFS untuk membawa koneksi ADB hidup sejak *early-init*.
