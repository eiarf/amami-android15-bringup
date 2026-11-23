#
# Copyright (C) 2014-2026 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

DEVICE_PATH := device/sony/amami

# Inherit from common rhine definitions
-include device/sony/rhine-common/BoardConfigCommon.mk

# Architecture (Pure 32-bit ARMv7-A NEON / Krait)
TARGET_CPU_ABI := armeabi-v7a
TARGET_CPU_ABI2 := armeabi
TARGET_ARCH := arm
TARGET_ARCH_VARIANT := armv7-a-neon
TARGET_CPU_VARIANT := krait
TARGET_NO_BOOTLOADER := true

# Platform
TARGET_BOARD_PLATFORM := msm8974
TARGET_BOOTLOADER_BOARD_NAME := amami
TARGET_OTA_ASSERT_DEVICE := D5503,amami,anami

# Hard Partition Boundaries (Sony Xperia Z1 Compact stock layout)
BOARD_FLASH_BLOCK_SIZE := 131072
BOARD_BOOTIMAGE_PARTITION_SIZE := 20971520        # 20 MiB (0x01400000)
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 20971520    # 20 MiB (0x01400000)
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 2436890624     # ~2.43 GiB
BOARD_USERDATAIMAGE_PARTITION_SIZE := 12891175936  # ~12.89 GiB
BOARD_CACHEIMAGE_PARTITION_SIZE := 209715200       # 200 MiB

BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

# Verified Boot (Disabled for legacy bootloader)
BOARD_AVB_ENABLE := false
AB_OTA_UPDATER := false

# Kernel Properties (MSM8974 3.4.113 Downstream)
TARGET_KERNEL_CONFIG := lineageos_rhine_amami_row_defconfig
TARGET_KERNEL_SOURCE := kernel/sony/msm8974
BOARD_KERNEL_BASE := 0x00000000
BOARD_KERNEL_PAGESIZE := 2048
BOARD_MKBOOTIMG_ARGS := --ramdisk_offset 0x02000000 --tags_offset 0x01E00000
BOARD_KERNEL_CMDLINE := console=ttyHSL0,115200,n8 androidboot.hardware=amami androidboot.bootdevice=msm_sdcc.1
BOARD_KERNEL_CMDLINE += androidboot.selinux=permissive
BOARD_KERNEL_SEPARATED_DT := true

# Graphics (Adreno 330 OpenGL ES 3.0 / SkiaGL)
TARGET_USES_VULKAN := false
TARGET_USES_ION := true
NUM_FRAMEBUFFER_SURFACE_BUFFERS := 3
MAX_VIRTUAL_DISPLAY_DIMENSION := 2048
TARGET_SCREEN_DENSITY := 320

# Strict Partition Budget & Memory Optimization
MALLOC_SVELTE := true
USE_DEX2OAT_DEBUG := false
DONT_DEXPREOPT_PREBUILTS := true
WITH_DEXPREOPT_DEBUG_INFO := false
WITH_DEXPREOPT_BOOT_IMG_AND_SYSTEM_SERVER_ONLY := true

# Relax artifact requirements for legacy 32-bit target
PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := relaxed

# QCOM SELinux Policies
-include device/qcom/sepolicy-legacy/sepolicy.mk
