# Limbo Emulator for Android

Limbo is a QEMU-based emulator for Android. It supports x86/x86-64, ARM/ARM64,
PowerPC/PowerPC64 and SPARC guests. The source tree currently uses the Limbo
QEMU 5.1.0 integration.

## Continuous integration

Every push and pull request runs `.github/workflows/android.yml`. The workflow
installs the pinned Android NDK and native build dependencies, downloads the
pinned QEMU/GLib/libffi/pixman/SDL source releases, applies Limbo's maintained
patches, builds the native runtime for ARM64 Android devices and all four guest
families, packages OVMF firmware, and assembles the four debug APK variants.
The APKs are published as the `limbo-android-arm64-guest-apks` workflow artifact.
This workflow has been authored in source; its first GitHub run is still needed
to validate the full toolchain end to end.

## UEFI guest support

The app bundles OVMF x86-64 firmware through CI. After installation, x86-64 VMs
use UEFI by default when both firmware files are available. Limbo creates a
separate persistent `OVMF_VARS` file for each VM, so firmware settings are not
shared across machines. Existing legacy BIOS images remain supported: add
`--limbo-uefi=off` to **Extra QEMU parameters** to disable automatic UEFI for a
VM. A custom `-bios` or explicit pflash configuration also takes precedence.
Other guest architectures retain their existing firmware configuration.

## Developer documentation

See [README.developers](README.developers) for manual native and Android builds.
Limbo is licensed under GPL-2.0; third-party dependencies and firmware retain
their own licenses. The OVMF license/copyright text is packaged with CI builds.
