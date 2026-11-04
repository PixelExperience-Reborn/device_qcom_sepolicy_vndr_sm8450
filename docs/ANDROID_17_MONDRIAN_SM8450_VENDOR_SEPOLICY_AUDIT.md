# P2 — Archived Qualcomm SM8450 vendor sepolicy: Android17 PE-Reborn/mondrian review

Date: 2026-11-04. **Source-only security review. This old CAF/Lineage vendor policy is NOT selected in Android17 manifest.**

## Provenance and actual Soong/Make ownership

- PixelExperience-Reborn `device_qcom_sepolicy_vndr_sm8450` archival `seventeen` commit `b6998a9ccb7ec8889b5ec4110c2ccf378b86111b` (2024-01-15). Source history merges Qualcomm `LA.VENDOR.1.0.r1-24300-WAIPIO.QSSI14.0` under `lineage-21.0-caf-sm8450`. This is Qualcomm/Lineage **Android14-era** policy, not an AOSP17 or independently authored PixelExperience-Reborn port.
- `SEPolicy.mk` assumes a separate source at `QSSI_SEPOLICY_PATH:= device/qcom/sepolicy`. That older generic Qualcomm project has already been independently reviewed and **blocked** due to parser-time CIL mutation and untrusted-app DSP/QSPM HAL permissions; this repo's SEPolicy.mk imports its `generic/public`, `generic/private`, `qva`, and product public/private paths, so it is **not standalone**.
- `SEPolicy.mk` appends broad `generic/vendor/common`, `generic/vendor/common/attribute`, `qva/vendor/ssg` and `qva/vendor/common` into `BOARD_VENDOR_SEPOLICY_DIRS`; it adds `generic/vendor/$(TARGET_BOARD_PLATFORM)` / `qva/vendor/$(TARGET_BOARD_PLATFORM)` or `$(TARGET_SEPOLICY_DIR)` based on product flags. It also unconditionally includes Qualcomm test policy directories for userdebug/eng variants. The archive contains **no directory named** `generic/vendor/sm8450` or `qva/vendor/sm8450`; this means the generic hardware-family naming cannot be relied on as a proven policy selection for a native mondrian product.
- The repo also contains `generic/vendor/anorak` rules for unrelated devices, and vendor integration macros for many HALs. Their existence is not evidence that those HAL services are installed on mondrian.

## High-risk examples — do not import without runtime evidence

- `generic/vendor/common/dontaudit.te` hides `vendor_qti_init_shell` `dac_override` and `vendor_modprobe` `proc_cmdline:file read` AVC denials. Masking denials prevents diagnosing new Android17 policy/boot failures. Do not include blanket historical dontaudit rules during initial bring-up.
- `generic/vendor/common/hal_keymint_qti.te` defines `vendor_hal_keymint_qti`, binds it to `hal_keymint`, grants access to `tee_device` and a secure DMA-BUF QSEECom heap, and suppresses firmware directory denials. **KeyMint, FBE/AVB and secure key material are security critical**. Verify vendor binaries, UDS/SIPC, actual KeyMint HAL instance, VINTF and SELinux service contexts rather than blindly adopting this domain and access.
- `generic/vendor/common/hal_audio_default.te` accesses vendor audio devices, firmware, persistent files, Bluetooth property and DSP; such permissions depend on exactly installed HAL binaries and driver nodes. Apply the same scrutiny to camera/graphics/modem/Wi-Fi/NFC and other broad common policy.
- `generic/vendor/common/file_contexts` labels numerous /dev paths including diag/IPA/DSP/QSEE; only verified nodes should have labels. Generic path patterns may collide with a new native device/product label layout.

## Native independent PE-Reborn design

1. Do **not** inherit Qualcomm CAF `SEPolicy.mk` or the old `device/qcom/sepolicy` package. The project must create its own `device/xiaomi/mondrian` and `device/xiaomi/sm8450-common` sources for Android17, with a small and correctly partition-scoped `BOARD_VENDOR_SEPOLICY_DIRS` (and ODM/product/system_ext only where needed).
2. The existing LF52406 LineageOS-derived device/common trees and vendor blobs may be inspected only as **hardware reference** for actual hardware nodes, init rc, KeyMint/TEE, DAL and VINTF services, not reused verbatim or inherited.
3. Inventory exact proprietary service executables and installed shared libraries, binder/hwbinder/AIDL declarations, `file_contexts`, `property_contexts`, `genfs_contexts` and `hwservice_contexts`. Use the minimum rules needed for a verified consumer. No `permissive` or blanket `allow`, and no blind suppression of AVC denials.
4. Compile against official AOSP17 `platform/system/sepolicy` commit/tag and actual new product `BOARD_VENDOR_SEPOLICY_DIRS`. Verify `neverallow`, `secilc`/policy compile, public policy API version mapping, Treble FCM/VINTF and SELinux enforcing CTS/VTS.
5. Run real mondrian boot and HAL tests; validate storage decryption/KeyMint, camera/audio/radio/Wi-Fi/BT/NFC, boot/recovery and OTA. A source audit does not certify secure boot.

## Evidence and release status

- [x] Historical CAF/Lineage QSSI14 provenance, dependencies and shared vendor/product policy directories identified.
- [x] Verified **no** `generic/vendor/sm8450` or `qva/vendor/sm8450` directory in archive.
- [x] KeyMint, dontaudit, generic node labels and broad audio policy risk examples identified.
- [x] Host-only archived QSSI14 KeyMint/vendor SELinux inventory [CI PASS #41802000101](https://github.com/PixelExperience-Reborn/device_qcom_sepolicy_vndr_sm8450/actions/runs/41802000101); the old Make file was never executed, and no policy was imported.
- [ ] AOSP17 native mondrian vendor policy created and compiled, with extracted real consumers.
- [ ] SELinux `neverallow`, VINTF/CTS/VTS and enforcing boot on mondrian proven.

**Decision:** exclude the archival `device/qcom/sepolicy_vndr/sm8450` tree from the staged AOSP17 manifest. Treat as a vendor HAL permission reference, never an approved finished Android17 vendor policy.
