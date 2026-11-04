#!/usr/bin/env python3
"""Host-only safety inventory of old CAF SM8450 vendor SELinux. Never executes Make."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]

def check(ok, label):
    if not ok: raise AssertionError(label)
    print("PASS legacy CAF vendor sepolicy:",label)

try:
    mk=(ROOT/"SEPolicy.mk").read_text()
    ignored=(ROOT/"generic/vendor/common/dontaudit.te").read_text()
    keymint=(ROOT/"generic/vendor/common/hal_keymint_qti.te").read_text()
    audio=(ROOT/"generic/vendor/common/hal_audio_default.te").read_text()
    paths=(ROOT/"generic/vendor/common/file_contexts").read_text()
    for anchor in ("QSSI_SEPOLICY_PATH:= device/qcom/sepolicy","BOARD_SYSTEM_EXT_PREBUILT_DIR",
                   "BOARD_PRODUCT_PREBUILT_DIR","SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS",
                   "SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS","PRODUCT_PUBLIC_SEPOLICY_DIRS",
                   "PRODUCT_PRIVATE_SEPOLICY_DIRS","BOARD_VENDOR_SEPOLICY_DIRS",
                   "TARGET_BOARD_PLATFORM","TARGET_SEPOLICY_DIR","TARGET_BUILD_VARIANT"):
        check(anchor in mk,"legacy Qualcomm Make dependency: "+anchor)
    check("generic/vendor/test" in mk and "qva/vendor/test" in mk,
          "legacy userdebug/eng vendor test policy auto-inclusion")
    check(not (ROOT/"generic/vendor/sm8450").exists()
          and not (ROOT/"qva/vendor/sm8450").exists(),
          "no verified sm8450-specific policy directory in old source")
    check("dontaudit vendor_qti_init_shell self:capability dac_override;" in ignored
          and "dontaudit vendor_modprobe proc_cmdline:file read;" in ignored,
          "old suppressions could hide permissions failures on new ROM")
    for rule in ("type vendor_hal_keymint_qti, domain;",
                 "hal_server_domain(vendor_hal_keymint_qti, hal_keymint)",
                 "tee_device:chr_file", "vendor_dmabuf_qseecom_heap_device"):
        check(rule in keymint,"security-critical archived KeyMint/TEE allowance: "+rule)
    check("vendor_diag_device" in paths and "vendor_ipa_dev" in paths and
          "vendor_qdsp_device" in paths, "old generic file labels need exact hardware nodes")
    check("vendor_audio_data_file" in audio and "vendor_sysfs_audio" in audio,
          "old audio policy grants depend on actual HALs")
    check((ROOT/"generic/vendor/anorak/file_contexts").is_file(),
          "archive also contains unrelated device-specific policy")
    print("PASS source-only. No old CAF policy activated; no full SELinux compile/VTS/boot.")
except (AssertionError,OSError) as err:
    print("FAIL:",err,file=sys.stderr)
    sys.exit(1)
