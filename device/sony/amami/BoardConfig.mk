#
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/sony/amami

# Architecture (32-bit ARMv7-A NEON / Krait)
TARGET_ARCH := arm
TARGET_ARCH_VARIANT := armv7-a-neon
TARGET_CPU_ABI := armeabi-v7a
TARGET_CPU_ABI2 := armeabi
TARGET_CPU_VARIANT := generic
TARGET_CPU_VARIANT_RUNTIME := krait

# Bootloader / Platform
TARGET_BOARD_PLATFORM := msm8974
TARGET_BOOTLOADER_BOARD_NAME := MSM8974

# Kernel (Mainline 6.16)
TARGET_KERNEL_SOURCE := kernel/sony/msm8974
TARGET_KERNEL_CONFIG := msm8974_defconfig
TARGET_KERNEL_CONFIG_EXT := $(DEVICE_PATH)/kernel-configs/amami_android17.config
TARGET_KERNEL_CLANG_COMPILE := true
BOARD_KERNEL_IMAGE_NAME := zImage
BOARD_KERNEL_APPEND_DTBS := qcom/qcom-msm8974-sony-xperia-rhine-amami.dtb
BOARD_KERNEL_ADDITIONAL_MAKE_FLAGS := INSTALL_MOD_COMPRESS=

# Kernel Command Line & Boot Image Layout (Sony Rhine / amami)
BOARD_KERNEL_BASE := 0x00000000
BOARD_KERNEL_PAGESIZE := 2048
BOARD_MKBOOTIMG_ARGS := --ramdisk_offset 0x02000000 --tags_offset 0x01E00000
BOARD_KERNEL_CMDLINE := androidboot.hardware=amami androidboot.boot_devices=soc/f9824900.mmc
BOARD_KERNEL_CMDLINE += androidboot.selinux=permissive
BOARD_KERNEL_CMDLINE += console=ttyMSM0,115200n8 earlycon

# Partitions (Sony Xperia Z1 Compact stock layout)
BOARD_FLASH_BLOCK_SIZE := 131072
BOARD_BOOTIMAGE_PARTITION_SIZE := 0x01400000
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 0x01400000
BOARD_RAMDISK_USE_XZ := true
BOARD_USES_FULL_RECOVERY_IMAGE := true
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 2436890624
BOARD_USERDATAIMAGE_PARTITION_SIZE := 12891175936
BOARD_CACHEIMAGE_PARTITION_SIZE := 209715200

BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_USERDATAIMAGE_FILE_SYSTEM_TYPE := f2fs
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true

# Graphics (Mainline DRM/KMS + Freedreno Adreno 330 + Minigbm + DRM HWC3)
BOARD_USES_DRM_HWCOMPOSER := true
TARGET_USES_HWC2 := true
$(call soong_config_set,minigbm,platform,msm)

# Wi-Fi (Mainline wcn36xx / hostapd)
$(call soong_config_set_bool,wpa_supplicant_8,wpa_build_hostapd,true)

# Mesa3D Freedreno (built via vendor/aospext Meson wrapper)
BOARD_BUILD_AOSPEXT_MESA3D := true
BOARD_MESA3D_SRC_DIR := external/mesa3d
BOARD_MESA3D_GALLIUM_DRIVERS := freedreno
BOARD_MESA3D_BUILD_LIBGBM := true

# Display / RenderEngine fallback
# Note: Adreno 330 (a3xx) only supports OpenGL ES 3.0 in Mesa Freedreno (no Vulkan/Turnip).
# Force SkiaGL for HWUI/RenderEngine; Android 17 still retains SkiaGLRenderEngine & SkiaOpenGLPipeline.
TARGET_USES_VULKAN := false

# Recovery
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/rootdir/etc/fstab.qcom

# SELinux (Permissive for initial mainline bringup)
BOARD_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# Allow legacy partition image generation without strict directory filtering
BUILD_BROKEN_INCORRECT_PARTITION_IMAGES := true

# amami is an A-only legacy partition device (Non-A/B)
AB_OTA_UPDATER := false
