# CHECKPOINT — Sony Xperia Z1 Compact (amami) (LineageOS 22.2 / Android 15)

- **Tanggal/Waktu:** 2026-11-23 19:41 WIB
- **Build ID:** `BP1A.250505.005` | **Target:** `lineage_amami-bp1a-userdebug`
- **Server:** `waffle.serverhive.in` (192 vCPU, 768 GB RAM) | Tree: `/serverhive5/eiarf/lineage-22`
- **Platform:** Sony Xperia Z1 Compact (`amami` / MSM8974 / 32-bit Krait ARMv7-a-neon)
- **Status Kompilasi & Flashing:** **BERHASIL 100% (EXIT CODE 0)** — `boot.img` (Rev 4) Flashed & Verified!

---

## 1. Verifikasi Artefak & Checksum SHA-256 (Tersimpan di `D:\z1c-a15\out\`)

| Artefak | Ukuran (Bytes) | Ukuran (MiB / GiB) | Batas Partisi | % Utilisasi | Status | SHA-256 Checksum |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`boot.img` (Rev 4 - Fixed Offset & Cmdline)** | `8,556,544` | ~8.16 MiB | `20,971,520` (20 MB) | **40.80%** | **FLASHED & PASS** | `c35a6d271ccd02748fed2dbac88de490469b6fea60e22e434041ff30ee41bf4d` |
| **`boot.img` (Rev 3 - lama)** | `8,556,544` | ~8.16 MiB | `20,971,520` (20 MB) | 40.80% | *Replaced* | `cdd90564ac908c2519c8bc224fdf561b3cbf9c7a11afb0e777ffc9fdddb8affe` |
| **`fotakernel.img` (TWRP referensi)** | `16,777,216` | 16.00 MiB | `20,971,520` (20 MB) | 80.00% | *Baseline* | `9a7516d7ca41f893dca9bf66ca096ff8b0ebfa82054ff837a7b8e11a12101859` |
| **`recovery.img`** | `19,290,112` | ~18.40 MiB | `20,971,520` (20 MB) | **91.98%** | **PASS** | `f41d09fbfcf18057a91709d2a53043bdd05f41fccda04102c9fafba72be7455a` |
| **`system.img`** | `1,594,438,152` | ~1.48 GiB | `2,436,890,624` (~2.43 GB) | **65.43%** | **INSTALLED** | *(Terkemas dalam flashable zip / terpasang di `mmcblk0p23`)* |
| **ROM Flashable Zip** | `770,200,124` | ~734.52 MiB | — | — | **PASS** | `063e53c113364b24ae6b067488e591d4d32a421b2d3d6988f21067a4266c8836` |

Salinan file lokal:
- [boot.img](file:///D:/z1c-a15/out/boot.img) *(SHA-256: `c35a6d271ccd02748fed2dbac88de490469b6fea60e22e434041ff30ee41bf4d`)*
- [fotakernel.img](file:///D:/z1c-a15/out/fotakernel.img)
- [recovery.img](file:///D:/z1c-a15/out/recovery.img)
- [lineage-22.2-20261123-UNOFFICIAL-amami.zip](file:///D:/z1c-a15/out/lineage-22.2-20261123-UNOFFICIAL-amami.zip)

---

## 2. Root Cause Triage & Perbaikan Kritis pada `boot.img` (Rev 4)

### A. Root Cause 1: Ramdisk Offset Mismatch (`0x02000000` vs `0x01000000`)
- **Fakta Binary:** Header dari `fotakernel.img` (TWRP yang terbukti bekerja di hardware ini) menggunakan:
  - `ramdisk_addr: 0x01000000` (16 MB offset)
  - `tags_addr: 0x01E00000` (30 MB offset)
- **Cacat pada Rev 3:** `BoardConfigCommon.mk` warisan dari commit lawas 2021 mendefinisikan `--ramdisk_offset 0x02000000` (32 MB). Di Sony S1 bootloader, ramdisk diletakkan setelah tags address (`32 MB > 30 MB`), menyebabkan bootloader gagal merelokasi ramdisk atau kernel tidak menemukan initrd pada pointer ATAGS.
- **Perbaikan:** Diubah menjadi `--ramdisk_offset 0x01000000` di `device/sony/rhine-common/BoardConfigCommon.mk`.

### B. Root Cause 2: Deadlock `earlyprintk` tanpa Hardware UART
- **Fakta Driver:** Pada MSM8974 kernel 3.4 (`arch/arm/kernel/early_printk.c`), fungsi `printch` melakukan polling register UART (`while (!(UART_SR & TXEMPTY))`). Tanpa kabel UART debug hardware dengan clock aktif, CPU membeku seketika (*dead hang*) di logo Sony pada pemanggilan `printk` pertama sebelum inisialisasi console.
- **Cacat pada Rev 3:** Parameter `earlyprintk` dan `androidboot.first_stage_console=1` aktif.
- **Perbaikan:** Dihapus sepenuhnya dari `BOARD_KERNEL_CMDLINE`.

### C. Root Cause 3: Restriksi Memori `vmalloc=300M`
- Pada 32-bit ARM (VMSPLIT_3G, batas 1GB lowmem), memaksa `vmalloc=300M` membatasi alokasi lowmem page tables kernel. Dihapus untuk membiarkan kernel menghitung kebutuhan vmalloc secara dinamis.

---

## 3. Komparasi Header Boot Image (Rev 4 vs TWRP Baseline)

| Header Parameter | `fotakernel.img` (TWRP Sukses) | `boot.img` (Rev 3 - Freeze) | `boot.img` (Rev 4 - Diperbaiki) |
| :--- | :--- | :--- | :--- |
| `kernel_addr` | `0x00008000` | `0x00008000` | `0x00008000` |
| `ramdisk_addr` | **`0x01000000`** | `0x02000000` (Mismatch) | **`0x01000000`** (Cocok) |
| `tags_addr` | `0x01E00000` | `0x01E00000` | `0x01E00000` |
| `page_size` | 2048 | 2048 | 2048 |
| `Appended DTB` | Ya (`0xd00dfeed`) | Ya (`0xd00dfeed`) | Ya (`0xd00dfeed`) |
| `earlyprintk` | Tidak ada | Ada (Hang trigger) | **Dihapus** |
| `vmalloc=300M` | Tidak ada | Ada | **Dihapus** |

---

## 4. Status Flashing ke Perangkat:
- Flashing ke `/dev/block/platform/msm_sdcc.1/by-name/boot` (`mmcblk0p14`): **BERHASIL 100%**.
- Checksum partisi terbaca ulang: `c35a6d271ccd02748fed2dbac88de490469b6fea60e22e434041ff30ee41bf4d` (Bit-for-bit matched).
