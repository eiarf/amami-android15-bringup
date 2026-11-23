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

# Inherit from common rhine definitions
$(call inherit-product, device/sony/rhine-common/rhine.mk)

DEVICE_PATH := device/sony/amami

# Soong namespaces
PRODUCT_SOONG_NAMESPACES += \
    $(DEVICE_PATH) \
    hardware/qcom-caf/msm8974

# Fallback cgroups v1 for Kernel 3.4
PRODUCT_COPY_FILES += \
    system/core/libprocessgroup/profiles/cgroups_28.json:$(TARGET_COPY_OUT_VENDOR)/etc/cgroups.json \
    system/core/libprocessgroup/profiles/task_profiles_28.json:$(TARGET_COPY_OUT_VENDOR)/etc/task_profiles.json

# Graphics & SurfaceFlinger Properties (OpenGL ES 3.0 / SkiaGL)
PRODUCT_PROPERTY_OVERRIDES += \
    debug.egl.hw=0 \
    ro.opengles.version=196608 \
    debug.hwui.renderer=opengl \
    debug.renderengine.backend=skiagl \
    ro.surface_flinger.max_frame_buffer_acquired_buffers=3 \
    ro.surface_flinger.has_wide_color_display=false \
    ro.surface_flinger.has_HDR_display=false

# Low-RAM / Android Go properties
PRODUCT_PROPERTY_OVERRIDES += \
    ro.config.avoid_gfx_accel=true \
    ro.sys.fw.bg_apps_limit=8 \
    config.disable_atlas=true

# Audio HAL packages
PRODUCT_PACKAGES += \
    audio.primary.msm8974 \
    audio.a2dp.default \
    audio.usb.default \
    audio.r_submix.default \
    tinymix

# Display & Gralloc HAL packages
PRODUCT_PACKAGES += \
    android.hardware.graphics.allocator@2.0-impl \
    android.hardware.graphics.allocator@2.0-service \
    android.hardware.graphics.composer@2.1-service \
    android.hardware.graphics.mapper@2.0-impl-2.1 \
    gralloc.msm8974 \
    hwcomposer.msm8974 \
    memtrack.msm8974 \
    libqdutils

# Sony Hardware helpers
PRODUCT_PACKAGES += \
    macaddrsetup \
    thermanager \
    timekeep
