# CHECKPOINT — amami (LineageOS-UL 20.0 / Android 13)

- **Tanggal/Waktu:** 2026-11-24 18:42 WIB
- **Build Status:** **STABLE & VERIFIED ON DEVICE** (Single-module fixes deployed & verified after reboot)
- **Device ID:** `CB5A1ZGCZ9` (Connected via USB ADB root)
- **Target Device:** Sony Xperia Z1 Compact (`amami` / MSM8974 / 32-bit Krait ARMv7)
- **ROM Tree:** LineageOS-UL 20.0 (Android 13 Tiramisu)
- **Kernel:** `3.4.113` | **SELinux:** Permissive (`androidboot.selinux=permissive`)

---

## 1. Do Not Break List (Status Verifikasi Live Setelah Reboot)
- [x] **Bootloader S1Boot & Init:** Lolos boot, ZRAM swap aktif 512 MiB di `/dev/block/zram0`.
- [x] **Display & Graphics:** 720x1280 @ 60Hz. SurfaceFlinger & HWComposer aktif via `HWC2On1Adapter`, GLES RenderEngine Adreno 330 aktif.
- [x] **Touchscreen & Gestures:** Synaptics ClearPad aktif, 10 multitouch pointer normal.
- [x] **Audio:** `audioserver` & HAL aktif, ACDB calibration ID 14, speaker output normal.
- [x] **Wi-Fi:** `wlan0` aktif, scan & asosiasi AP normal.
- [x] **Bluetooth:** **FIXED & VERIFIED!** `state: ON`, address `44:D4:E0:76:6F:B0`, `Bluetooth crashed 0 times`.
- [x] **Telephony / RIL / IMEI:** **FIXED & VERIFIED!** `com.android.phone` berjalan tanpa ANR, `DEVICE_IDENTITY` sukses membaca IMEI (`SVN: 3D`), `radioStateChanged: 1` (Radio ON), `iphonesubinfo` aktif.
- [x] **Contacts / `android.process.acore`:** **FIXED & VERIFIED!** Berjalan tanpa crash loop / NPE.
- [x] **Crash & Tombstone Audit:** `logcat -b crash -d` = **0**, `/data/tombstones/` = **0**, `/data/anr/` = **0**.

---

## 2. Perbaikan yang Diterapkan & Disinkronkan ke `patches/`

1. **IMEI / RIL / `com.android.phone` ANR (`IOemHook` deadlock):**
   - **Akar Masalah:** `device/sony/msm8974-common/treble-manifest-radio.xml` mendeklarasikan `android.hardware.radio.deprecated@1.0::IOemHook`, padahal `rild` hanya mendaftarkan `IRadio@1.1` dan `ISap@1.1`. `HwBinder.getService("slot1", true)` menunggu tanpa batas waktu sehingga `com.android.phone` terkena ANR berulang sebelum sempat menginisialisasi `PhoneFactory` / `iphonesubinfo` / Radio.
   - **Patch:** [0001-msm8974-common-all-fixes.patch](file:///D:/z1c-a13/patches/device_sony_msm8974-common/0001-msm8974-common-all-fixes.patch)
   - **Target Kompilasi:** `vendor_manifest.xml` -> `/vendor/etc/vintf/manifest.xml`

2. **Bluetooth `com.android.bluetooth` Crash Loop (`SIGABRT`):**
   - **Akar Masalah:** `packages/modules/Bluetooth/system/stack/btu/btu_task.cc` memanggil `LOG(FATAL)` saat `EnableRealTimeScheduling()` gagal (`sched_setscheduler(SCHED_FIFO)` ditolak `-EPERM` pada kernel 3.4 untuk UID 1002).
   - **Patch:** [0001-btu_task-do-not-fatal-on-rt-scheduling-failure.patch](file:///D:/z1c-a13/patches/packages_modules_Bluetooth/0001-btu_task-do-not-fatal-on-rt-scheduling-failure.patch) (`LOG(FATAL)` -> `LOG(WARNING)`)
   - **Target Kompilasi:** `com.android.btservices` -> `/system/apex/com.android.btservices/lib/libbluetooth_jni.so`

3. **`android.process.acore` Crash Loop (`NullPointerException`):**
   - **Akar Masalah:** `packages/providers/ContactsProvider/src/com/android/providers/contacts/util/SelectionBuilder.java` mengirim `null` sebagai argumen ke-3 `SQLiteTokenizer.tokenize(...)`, memicu NPE pada `checker.accept(token)` di `SQLiteTokenizer.java:108`.
   - **Patch:** [0001-SelectionBuilder-avoid-null-consumer-NPE.patch](file:///D:/z1c-a13/patches/packages_providers_ContactsProvider/0001-SelectionBuilder-avoid-null-consumer-NPE.patch) (`null` -> `token -> {}`)
   - **Target Kompilasi:** `ContactsProvider` -> `/system/priv-app/ContactsProvider/ContactsProvider.apk`

---

## 3. Catatan Penting (Parity Gate)
Ketiga perbaikan di atas sudah **aktif di HP Anda saat ini** (via `adb push` + `adb reboot`) dan **sudah tersinkron di source tree server & folder `D:\z1c-a13\patches\`**.
Jika Anda ingin membuat file `.zip` ROM final terbaru yang sudah menyertakan ketiga perbaikan ini di lain waktu (saat server tidak sibuk dengan build ROM project lain), cukup jalankan `m bacon` di server.
