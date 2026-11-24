#
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit 32-bit ARM base product
# Note: LineageOS 24.0 dropped official 32-bit ARM support; check vendor/lineage
# on the build server and relax artifact path checks if needed.
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_arm.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit LineageOS common configuration (if building LineageOS 24.0)
$(call inherit-product-if-exists, vendor/lineage/config/common_full_phone.mk)

# Inherit amami mainline device configuration
$(call inherit-product, device/sony/amami/device.mk)

# Relax artifact path requirements for custom 32-bit mainline bringup
PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := false

# Device identifier
PRODUCT_NAME := lineage_amami
PRODUCT_DEVICE := amami
PRODUCT_BRAND := Sony
PRODUCT_MODEL := Xperia Z1 Compact
PRODUCT_MANUFACTURER := Sony

PRODUCT_GMS_CLIENTID_BASE := android-sony

# Disable dynamic partitions for legacy eMMC static layout
PRODUCT_USE_DYNAMIC_PARTITIONS := false
