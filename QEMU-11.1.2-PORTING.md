# QEMU 11.1.2 port assessment

## Scope

This branch is an isolated migration effort. Keep `master` on QEMU 5.1.0 until the modern build produces installable APKs and runtime checks pass.

Target: upstream QEMU 11.1.2, the stable release listed by the official QEMU download page.

## Findings from the existing Limbo build

1. **QEMU is deeply integrated, not just downloaded.** The build applies `patches/qemu-5.1.0.patch`, which changes Android-specific behavior in the SDL2 display/input path, VNC key handling and refresh rate, POSIX/PTY behavior, and other core files. These changes must be rebased individually; the old patch must not be applied to QEMU 11.
2. **The build scripts assume the old build layout.** `Makefile` modifies `qemu/x86_64-softmmu/qemu-system-x86_64`, copies old-style `.libs/*.so` outputs, and expects ROMs under `qemu/pc-bios`. QEMU's modern build is Meson/Ninja-backed; configure/build output locations and dependency discovery need revalidation.
3. **Configuration is explicitly version-gated.** `android-qemu-config.mak` accepts only 2.9.1 and 5.1.0. The generic options include legacy configure flags; we must validate each flag against QEMU 11.1.2 rather than assuming they still exist.
4. **Dependencies are coupled to the old build.** Limbo currently builds GLib 2.56.1, libffi 3.3, Pixman 0.40.0 and SDL2 2.0.8 separately, with Android-specific patches and custom include/link flags. QEMU 11's dependency requirements and SDL integration need a deliberate plan.
5. **Four guest targets and four Android host ABIs matter.** The intended guest targets are x86_64, aarch64, ppc64 and sparc; APK modules target arm64-v8a, armeabi-v7a, x86 and x86_64. A single successful arm64 build is not sufficient to call the port complete.

## Port strategy

- Keep this branch separate from `master`; do not switch the production workflow to QEMU 11 until it passes.
- First make a version-specific QEMU 11 configure/build path using the modern configure + Meson/Ninja build model and the Android NDK toolchain.
- Rebase Limbo's behavioral patches one at a time, with clear patch names and comments. Do not carry unrelated upstream modifications forward.
- Update library staging, QEMU binary/library discovery, ROM/keymap packaging, and version metadata for the actual QEMU 11 build outputs.
- Build and package each Android ABI and each supported guest target; then test boot, disk I/O, networking, display, keyboard/mouse input, pause/resume, audio, and firmware/ROM availability.
- Keep the QEMU 5.1.0 path available until QEMU 11.1.2 passes both CI and device-level smoke tests.

## Important baseline observation

The latest workflow run at the time this assessment was prepared completed the native QEMU/dependency build and OVMF packaging, then failed during the Gradle APK build. Therefore, native QEMU 5.1.0 compilation and Android APK packaging are separate validation gates; the Gradle failure should be diagnosed independently and not mistaken for a QEMU compiler failure.

## Upstream references

- QEMU 11.1.2 release: https://www.qemu.org/download/
- QEMU 11.1.2 build environment: https://qemu.readthedocs.io/en/v11.1.2/devel/build-environment.html
- QEMU build-system documentation: https://qemu.readthedocs.io/en/v11.1.2/devel/build-system.html
