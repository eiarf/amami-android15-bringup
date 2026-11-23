# LineageOS 22.2 (Android 15) Port for Sony Xperia Z1 Compact (`amami`)

Technical documentation, BSP architecture analysis, local manifests, device tree configs, and patch sets for bringing up **Android 15 (LineageOS 22.2)** on the legacy **Sony Xperia Z1 Compact (`amami` / MSM8974)**.

---

## 1. Technical Feasibility Analysis

### Can Android 15 Run on MSM8974?
**Yes, experimentally**, but **not** out of the box using existing Android 12 / LineageOS 19.0 trees (`115ek/manifest`).

In Android 15 (LineageOS 22.x), Google and LineageOS introduced significant core platform changes that break legacy 32-bit Qualcomm BSPs:

| Component / Subsystem | State in LineageOS 19.0 (A12) | Challenges in LineageOS 22.2 (A15) | Applied BSP Engineering Fix |
|---|---|---|---|
| **32-bit CPU Support** | Maintained semi-officially in AOSP | LineageOS 22 dropped 32-bit targets; AOSP requires 64-bit | Set `TARGET_ARCH := arm`, `armv7-a-neon`, `PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := relaxed` |
| **eBPF & Networking** | Basic BPF shims (repopick `320591`) | `bpfloader` strictly halts `init` and `netd` on failure | Patched `BpfLoader.cpp` to downgrade failure to a graceful warning |
| **Graphics & Vulkan** | Adreno 330 OpenGL ES 3.0 via CAF display | Android 15 UI pushes Vulkan (SkiaVK/Turnip) by default | Adreno 330 lacks Vulkan hardware support; forced `debug.hwui.renderer=opengl` and `SkiaGL` |
| **Display HAL (HWC)** | Relied on legacy libskia symbols | Modern Skia headers and render engine symbols changed | Injected Skia RenderEngine compatibility shims (Kyle Harrison patch) into CAF HWC |
| **Physical Partition Limits** | System partition fit with modest headroom | Default LineageOS 22 system build exceeds 2.5 GB | Amami `/system` partition is capped at **2.43 GB**. Enabled `MALLOC_SVELTE := true` and trimmed bloat via `debloat_lowram.xml` |

---

## 2. Architecture Paths

### Path A: Modernized Downstream Kernel 3.4.113 (Recommended)
- **Kernel:** `115ek/android_kernel_sony_msm8974` (branch `lineage-19.0-WIP`).
- **HAL:** Qualcomm CAF MSM8974 Display, Audio, Media + Sony proprietary vendor blobs.
- **Advantages:** Full hardware compatibility with Sony proprietary hardware (IMX220 Camera HAL1, WCD9320 Audio, RIL/Modem, Wi-Fi).
- **Challenges:** Requires userspace eBPF bypass, cgroups v1 fallback (`cgroups_28.json`), backported `renameat2`, and UTS version spoofing.
- **Reference:** Proven functional on the same SoC (MSM8974 / Snapdragon 800) by developer `acroreiser` on the LG Nexus 5 (`hammerhead`) up to LineageOS 22.2.

### Path B: Mainline Linux Kernel 6.x (`msm8974-mainline`) + Mesa Freedreno
- **Kernel:** Mainline Linux (6.6 LTS / 6.16) + Mesa Freedreno (OpenGL ES 3.0) + DRM HWC3.
- **Advantages:** Native eBPF, native cgroups v2, native memfd.
- **Challenges:** Sony IMX220 camera is incomplete on mainline, complex ALSA UCM audio topology, and requires chained `lk2nd` bootloader.

---

## 3. Repository Structure

```text
├── CHECKPOINT.md                       # Single Source of Truth & forensic boot log
├── README.md                           # Technical overview and execution guide
├── local_manifests/
│   ├── amami_lineage22.xml             # Remote repository definitions for repo sync
│   └── debloat_lowram.xml              # Package removal manifest for partition budget
├── device/
│   └── sony/
│       └── amami/
│           ├── AndroidProducts.mk      # Lunch target definitions
│           ├── lineage_amami.mk        # Android Go low-RAM profile & device specs
│           ├── BoardConfig.mk          # 32-bit Krait, 2.43GB partition budget, SkiaGL
│           └── device.mk               # HAL packages, properties, cgroups fallback
├── patches/
│   ├── amami_all_changes.patch         # Exported device tree diffs
│   ├── rhine-common_all_changes.patch  # Common Rhine board config & init fixes
│   ├── msm8974-common_all_changes.patch# Common MSM8974 HAL & shim patches
│   ├── kernel_all_changes.patch        # Kernel appended DTB, renameat2, UTS spoofing
│   ├── bpf/                            # Bpfloader legacy bypass
│   ├── display/                        # CAF display SkiaGL compatibility
│   └── build/                          # Artifact path requirements overrides
└── scripts/
    ├── apply_patches.sh                # Idempotent patch applier
    ├── build_bootimage.py              # Remote automated bootimage builder
    ├── build_single_module.sh          # Single-module build runner
    ├── check_git_repos.py              # Git status inspector across server trees
    ├── download_boot.py                # Automated SFTP boot.img downloader
    ├── fix_appended_dtb.py             # DTB appending and defconfig patcher
    ├── fix_syscalls.py                 # renameat2 syscall (#382) injector
    └── run_ssh.py                      # Headless Paramiko SSH runner
```

---

## 4. Build Server Setup & Execution

Execute following the **Strict Single-Module Build Policy**:

```bash
# 1. Initialize LineageOS 22.1 (Android 15) source tree
mkdir -p ~/android/lineage-22 && cd ~/android/lineage-22
repo init -u https://github.com/LineageOS/android.git -b lineage-22.1 --git-lfs

# 2. Add local manifests
mkdir -p .repo/local_manifests
cp /path/to/amami_lineage22.xml .repo/local_manifests/amami.xml
cp /path/to/debloat_lowram.xml .repo/local_manifests/debloat.xml

# 3. Synchronize trees (shallow sync)
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags

# 4. Copy device tree & apply patches
cp -r /path/to/device/sony/amami device/sony/amami
bash /path/to/scripts/apply_patches.sh

# 5. Build environment setup & lunch
source build/envsetup.sh
lunch lineage_amami-bp1a-userdebug

# Step A: Compile Kernel & Boot Image
mka bootimage

# Step B: Compile Core Hardware HALs
mka hwcomposer.msm8974 gralloc.msm8974 audio.primary.msm8974

# Step C: Build Full Flashable ROM (Only after bootloader and init stages pass)
# mka bacon
```

---

## 5. Bring-Up Forensics & Key Technical Fixes

Detailed step-by-step logs, binary checksum verifications, and partition calculations are tracked in [CHECKPOINT.md](CHECKPOINT.md).

### Critical Issues Resolved:

1. **Appended DTB (`zImage-dtb`):**
   - The legacy Sony S1 bootloader on Rhine (MSM8974) **does not parse QCDT tables (`dt.img`)**.
   - Enabled `CONFIG_ARM_APPENDED_DTB=y` and `BOARD_KERNEL_IMAGE_NAME := zImage-dtb`. Appended DTB magic `0xd00dfeed` verified at kernel offsets `0x606dd8` and `0x63e60c`.

2. **Ramdisk Load Offset (`0x01000000`):**
   - Forensic header analysis of working recovery (`fotakernel`) showed S1 bootloader loads the ramdisk at **16 MB (`0x01000000`)** and ATAGS at **30 MB (`0x01E00000`)**.
   - An outdated 2021 bringup hack specified `--ramdisk_offset 0x02000000` (32 MB), placing the ramdisk past the tags address and causing immediate bootloader relocation failure. Corrected to `--ramdisk_offset 0x01000000`.

3. **Kernel Command Line Deadlock (`earlyprintk`):**
   - On MSM8974 downstream 3.4 (`arch/arm/kernel/early_printk.c`), `printch` continuously polls the UART TX FIFO status register (`while (!(UART_SR & TXEMPTY))`).
   - Without an active hardware UART debug cable, the unclocked register deadlocks the CPU on the first `printk`. Removed `earlyprintk`, `androidboot.first_stage_console=1`, and `vmalloc=300M` from `BOARD_KERNEL_CMDLINE`.

4. **Syscall `renameat2` (ARM Syscall #382) & UTS Spoofing:**
   - Android 15 `first_stage_init` requires `renameat2(..., RENAME_NOREPLACE)`. Wired syscall #382 in `arch/arm/kernel/calls.S` and backported implementation in `fs/namei.c`.
   - Spoofed kernel version to `4.9.337` in `include/linux/utsname.h` to bypass platform minimum kernel version assertions.

5. **Physical Partition Budget:**
   - `/boot`: `8,556,544` bytes (~8.16 MiB) / `20,971,520` bytes limit (**40.80%** utilization).
   - `/system`: `1,594,438,152` bytes (~1.48 GiB) / `2,436,890,624` bytes limit (**65.43%** utilization).
   - ROM Flashable Zip: `770,200,124` bytes (~734.52 MiB).
