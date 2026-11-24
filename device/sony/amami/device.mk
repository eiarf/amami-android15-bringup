#
# Copyright (C) 2026 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

LOCAL_PATH := device/sony/amami

# Screen density (720x1280 4.3" = ~342 dpi, XHDPI)
PRODUCT_AAPT_CONFIG := normal
PRODUCT_AAPT_PREF_CONFIG := xhdpi
PRODUCT_PROPERTY_OVERRIDES += \
    ro.sf.lcd_density=320

# Use memfd instead of ashmem (mainline 6.16 has no ashmem driver)
PRODUCT_PROPERTY_OVERRIDES += \
    sys.use_memfd=true

# Graphics: Mesa Freedreno + DRM HWC3 + Minigbm (MSM)
# Note: Adreno 330 has no Vulkan (Turnip starts at a6xx); force SkiaGL.
PRODUCT_PROPERTY_OVERRIDES += \
    ro.hardware.egl=mesa \
    ro.hardware.gralloc=minigbm_msm \
    ro.hardware.hwcomposer=drm \
    debug.hwui.renderer=skiagl \
    debug.renderengine.backend=skiaglthreaded \
    ro.opengles.version=196608

PRODUCT_PACKAGES += \
    android.hardware.graphics.allocator-service.minigbm \
    mapper.minigbm \
    gralloc.minigbm_msm \
    libminigbm_gralloc_msm \
    android.hardware.composer.hwc3-service.drm

# Mesa3D Gallium Freedreno targets (built via vendor/aospext)
PRODUCT_PACKAGES += \
    libEGL_mesa \
    libGLESv1_CM_mesa \
    libGLESv2_mesa \
    libgallium_dri

# Init, ueventd & fstab
PRODUCT_COPY_FILES += \
    device/sony/amami/rootdir/etc/fstab.qcom:$(TARGET_COPY_OUT_VENDOR)/etc/fstab.qcom \
    device/sony/amami/rootdir/etc/fstab.qcom:$(TARGET_COPY_OUT_RAMDISK)/fstab.qcom \
    device/sony/amami/rootdir/etc/init.amami.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/init.amami.rc \
    device/sony/amami/rootdir/etc/ueventd.amami.rc:$(TARGET_COPY_OUT_VENDOR)/etc/ueventd.rc

# Wi-Fi (Mainline wcn36xx)
PRODUCT_PACKAGES += \
    libwpa_client \
    wpa_supplicant \
    hostapd \
    wificond

PRODUCT_PROPERTY_OVERRIDES += \
    wifi.interface=wlan0 \
    wifi.supplicant_scan_interval=15

# Mainline Firmware Blobs (Adreno a330, WCNSS wcn3680, ADSP, Modem)
AMAMI_FW_RHINE := vendor/sony/amami-fw/rhine-common/proprietary/etc/firmware
AMAMI_FW_AMAMI := vendor/sony/amami-fw/amami/proprietary/etc/firmware

PRODUCT_COPY_FILES += $(foreach f, $(wildcard $(AMAMI_FW_RHINE)/a330_* $(AMAMI_FW_RHINE)/wcnss.*), \
    $(f):$(TARGET_COPY_OUT_VENDOR)/firmware/$(notdir $(f)))

PRODUCT_COPY_FILES += $(foreach f, $(wildcard $(AMAMI_FW_AMAMI)/adsp.* $(AMAMI_FW_AMAMI)/mba.* $(AMAMI_FW_AMAMI)/modem.*), \
    $(f):$(TARGET_COPY_OUT_VENDOR)/firmware/$(notdir $(f)))

# Permissions
PRODUCT_COPY_FILES += \
    frameworks/native/data/etc/android.hardware.touchscreen.multitouch.jazzhand.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.touchscreen.multitouch.jazzhand.xml \
    frameworks/native/data/etc/android.hardware.wifi.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.wifi.xml \
    frameworks/native/data/etc/android.hardware.bluetooth_le.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.bluetooth_le.xml \
    frameworks/native/data/etc/android.hardware.usb.host.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.hardware.usb.host.xml \
    frameworks/native/data/etc/android.software.opengles.deqp.level-2021-03-01.xml:$(TARGET_COPY_OUT_VENDOR)/etc/permissions/android.software.opengles.deqp.level.xml

# VINTF Manifest
DEVICE_MANIFEST_FILE += \
    device/sony/amami/configs/vintf/manifest.xml
