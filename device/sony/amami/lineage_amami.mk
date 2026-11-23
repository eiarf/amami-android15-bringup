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

# Inherit from amami device definition
$(call inherit-product, device/sony/amami/device.mk)

# Inherit common Lineage telephony & phone config
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

# Android Go / Low RAM optimizations (Essential for 2GB RAM & 2.43GB system budget)
PRODUCT_USE_PROFILE_GMS_GO := true
PRODUCT_PROPERTY_OVERRIDES += \
    ro.config.low_ram=true \
    ro.lmk.low_ram=true \
    ro.config.max_starting_bg=4 \
    dalvik.vm.jit.codecachesize=0 \
    dalvik.vm.heapgrowthlimit=128m \
    dalvik.vm.heapsize=256m

# Device identifiers
PRODUCT_NAME := lineage_amami
PRODUCT_DEVICE := amami
PRODUCT_BRAND := Sony
PRODUCT_MODEL := Xperia Z1 Compact
PRODUCT_MANUFACTURER := Sony
PRODUCT_BUILD_PROP_OVERRIDES += \
    PRODUCT_NAME=amami \
    BUILD_FINGERPRINT="Sony/D5503/D5503:5.1.1/14.6.A.1.236/2032950551:user/release-keys" \
    PRIVATE_BUILD_DESC="D5503-user 5.1.1 14.6.A.1.236 2032950551 release-keys"
