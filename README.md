# Sony Xperia Z1 Compact (`amami`) — Android 17 (LineageOS 24.0) + Mainline Kernel 6.16

Direktori ini berisi hasil analisis teknis, local manifest, skeleton device tree, dan kernel config fragment untuk eksperimen build **Android 17 / LineageOS 24.0** dengan kernel **Linux 6.16** (`msm8974-mainline/linux`, branch `qcom-msm8974-6.16.y`) untuk **Sony Xperia Z1 Compact (`amami`)**.

---

## 1. Ringkasan Analisis Kelayakan (Feasibility)

Membangun Android 17 + Kernel 6.16 untuk `amami` **bisa dikompilasi sebagai eksperimen bring-up**, tetapi **tidak bisa langsung memakai manifest/device-tree lama dari `115ek/manifest`**. Ada 4 perubahan arsitektur besar:

### A. Mengapa `115ek/manifest` (`lineage-19.0`) Tidak Bisa Dipakai Langsung
| Komponen | `115ek/manifest` (Lama) | Target Baru (Android 17 + Kernel 6.16) |
|---|---|---|
| Kernel | `115ek/android_kernel_sony_msm8974` (3.4 downstream) | `msm8974-mainline/linux` (`qcom-msm8974-6.16.y`, v6.16.12) |
| Graphics / HWC | `hardware/qcom-caf/msm8974/display` + Adreno blobs | `external/mesa3d` (Freedreno a3xx) + `external/minigbm` (`msm`) + `external/drm_hwcomposer` (HWC3) |
| Audio & Media | `hardware/qcom-caf/msm8974/audio` & `media` | Mainline ALSA (`tinyalsa`) + AOSP software codecs (`mediaswcodec`) |
| Shared Memory | `ashmem` driver (`/dev/ashmem`) | `memfd` (`CONFIG_MEMFD_CREATE=y` + `sys.use_memfd=true`) |
| Block Device Path | `/dev/block/platform/msm_sdcc.1/by-name/*` | `/dev/block/platform/soc/f9824900.mmc/by-name/*` |
| DTB Packaging | `BOARD_KERNEL_SEPARATED_DT := true` (`dtbToolLineage`) | `zImage-dtb` (appended DTB) atau `lk2nd` |

### B. Status Kernel Mainline 6.16 (`qcom-msm8974-6.16.y`) untuk `amami`
Hasil inspeksi langsung `arch/arm/boot/dts/qcom/qcom-msm8974-sony-xperia-rhine-amami.dts` dan `qcom-msm8974-sony-xperia-rhine.dtsi`:
- **Sudah ada di upstream 6.16:**
  - `sdhc_1` (eMMC), `sdhc_2` (microSD), `usb` + `usb_hs1_phy`
  - `gpio-keys` (volume + camera shutter/focus)
  - `smbb` battery charger, `pm8941_wled` (backlight), `pm8941_lpg` (LED)
  - `syna,rmi4-i2c` (touchscreen), `nxp,pn544-i2c` (NFC)
  - `remoteproc_adsp` & `remoteproc_mss`, `ramoops`
- **BELUM ada di DTS `rhine`/`amami` 6.16 (Patch sudah disiapkan di `patches/kernel-6.16/`):**
  1. **Display & Panel (`&mdss`, `&mdss_dsi0`, `&mdss_dsi0_phy`, `panel@0`):** Di `drivers/gpu/drm/panel/msm8974-generated/`, baru ada `panel-sony-leo-novatek-lgd.c`. Patch `0002` menambahkan driver `panel-sony-amami-novatek.c` (mendukung varian panel JDI & AUO 720p dari `dsi-panel-amami.dtsi`), dan patch `0001` mengaktifkan `&mdss`, `&mdss_dsi0`, `&mdss_dsi0_phy`, `panel@0` (`pm8941_wled`, reset GPIO 58, TE GPIO 12).
  2. **GPU (`&gpu`):** Patch `0001` mengaktifkan `&gpu` (Adreno 330) di `qcom-msm8974-sony-xperia-rhine.dtsi`.
  3. **Wi-Fi / BT (`&pronto`):** Patch `0001` mengaktifkan `&pronto` (`wcn3680`, regulator `pm8941_l6/l11/l19/s3`, `pm8841_s1`, dan `wcnss_pin_a` GPIO 35–44) di `qcom-msm8974-sony-xperia-rhine.dtsi`.
  4. **Masih perlu dikerjakan nanti:** Audio (`&sound` WCD9320) dan bootloader `lk2nd` untuk `amami` (jika bootloader Sony stock menolak `zImage-dtb` tanpa `qcom,msm-id`).

### C. Status Android 17 / LineageOS 24.0 pada `armv7` (32-bit) & Adreno 330
1. **32-bit ARM (`arm`):** LineageOS 24.0 sudah menghentikan dukungan resmi perangkat 32-bit. Namun di AOSP `android-17.0.0_r1` masih terdapat `target/product/aosp_arm.mk` (yang juga menyetel `PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := relaxed` untuk `aosp_arm`). Pada LineageOS 24.0, kemungkinan diperlukan patch kecil di `vendor/lineage` jika ada check yang memblokir `TARGET_ARCH := arm`.
2. **Graphics (No Vulkan pada Adreno 330):** Android 17 mendorong Vulkan (`SkiaVK` / ANGLE), namun Adreno 330 (`a3xx`) di Mesa Freedreno hanya mendukung OpenGL ES 3.0 (driver Vulkan Turnip baru mendukung `a6xx` ke atas). Untungnya di AOSP `android-17.0.0_r1`, `SkiaGLRenderEngine` (`frameworks/native/libs/renderengine/skia/`) dan `SkiaOpenGLPipeline` (`frameworks/base/libs/hwui/pipeline/skia/`) **masih ada**, sehingga `BoardConfig.mk` dan `device.mk` dikonfigurasi untuk memaksa `skiagl` (`TARGET_USES_VULKAN := false`).
3. **Partisi `system`:** Partisi `system` stock `amami` berukuran **~2.43 GB** (`2436890624` bytes). Jangan sertakan GApps ke `/system`; gunakan build `lineage_amami-userdebug` minimal (atau Pico/MindTheGapps hanya jika muat).

---

## 2. Struktur File yang Sudah Disiapkan di Local (`D:\z1c-a17`)

- `local_manifests/amami_lineage24_mainline.xml` — Local manifest untuk `repo sync` kernel 6.16.
- `device/sony/amami/` — Skeleton device tree Android 17 + Mainline 6.16:
  - `AndroidProducts.mk` & `lineage_amami.mk`
  - `BoardConfig.mk` (ARMv7-a-neon, Clang kernel build, `zImage-dtb`, `minigbm` `msm`, `drm_hwcomposer`, partisi `amami`)
  - `device.mk` (memfd, SkiaGL, DRM HWC3, Minigbm AIDL/Mapper, permissions)
  - `rootdir/etc/fstab.qcom` (path eMMC mainline `soc/f9824900.mmc`)
  - `rootdir/etc/init.amami.rc` (`sys.use_memfd true` & permission `/dev/dri/*`)
  - `configs/vintf/manifest.xml`
  - `kernel-configs/amami_android17.config` (fragment untuk `msm8974_defconfig`)
- `ref/` — Repository referensi hasil clone lokal (`115ek/manifest`, `kernel-6.16` sparse, `k-downstream` sparse, `glodroid_device`, `pine64-pinephone`, `aospext`, `lk2nd`).

---

## 3. Langkah Eksekusi di Build Server (Setelah Anda Approve)

```bash
# 1. Init LineageOS 24.0 (Android 17)
mkdir -p ~/android/lineage-24 && cd ~/android/lineage-24
repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 --git-lfs

# 2. Pasang local manifest
mkdir -p .repo/local_manifests
cp /path/to/amami_lineage24_mainline.xml .repo/local_manifests/amami.xml

# 3. Sync source
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags

# 4. Copy device tree & apply patch kernel 6.16 dari local D:\z1c-a17\
mkdir -p device/sony
cp -r /path/to/device/sony/amami device/sony/amami
git -C kernel/sony/msm8974 apply /path/to/patches/kernel-6.16/0001-arm-dts-qcom-msm8974-amami-enable-gpu-mdss-pronto.patch
git -C kernel/sony/msm8974 apply /path/to/patches/kernel-6.16/0002-drm-panel-msm8974-add-sony-amami-novatek-driver.patch

# 5. Test compile kernel 6.16 & bootimage dulu sebelum full ROM
source build/envsetup.sh
lunch lineage_amami-userdebug
m bootimage
```

> **Catatan sebelum build full ROM (`mka bacon`):**
> 1. `external/mesa3d/Android.bp` di AOSP 17 tidak menyediakan modul `libEGL_mesa`/`libGLESv*_mesa`/`libgallium_dri` untuk Freedreno, sehingga `vendor/aospext` (`GloDroid/aospext`) sudah ditambahkan ke local manifest untuk mem-build Mesa Freedreno via Meson. Pastikan paket host `meson`, `ninja-build`, `python3-mako`, `pkg-config` terpasang di build server.
> 2. Patch `0001` dan `0002` di `patches/kernel-6.16/` sudah mencakup `&gpu`, `&mdss`/`&mdss_dsi0` + driver panel `amami`, dan `&pronto`. Yang masih tersisa untuk dibawa ke tahap berikutnya adalah audio (`&sound` WCD9320) dan `lk2nd` (jika bootloader stock menolak `zImage-dtb`).

---

## 4. Lokasi File Kompilasi & Binari (Offline / Local)

Karena server build remote sudah kedaluwarsa, seluruh file binari hasil kompilasi telah dicadangkan secara lokal di:
`D:\Custom Rom's Stuff\Project Custom Rom Sony Xperia Z1 Compact\`

Daftar file binari siap pakai:
- `lineage-24.0-20261120-UNOFFICIAL-amami.zip` (827.29 MB - Full Flashable ROM)
- `system.img` (2.41 GB - Raw ext4 Android 17 system partition)
- `boot.img` & `boot_display_fixed.img` (Kernel Mainline 6.16 + DTB dual bank + Android 17 ramdisk)
- `recovery.img` (18.34 MB - Lineage Recovery Android 17)
- `twrp-3.4.0-1-amami.img` (14.4 MB - Working Recovery untuk FOTAKernel)
