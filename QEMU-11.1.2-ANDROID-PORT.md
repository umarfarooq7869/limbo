# QEMU 11.1.2 Android integration contract

## Why the Linux smoke test is not an APK build

The Linux smoke test proves that upstream QEMU 11.1.2 configures and builds its standalone emulator executables. Limbo does not launch those executables as subprocesses. Its JNI bridge uses `dlopen()` and resolves QEMU entry points and Limbo-specific globals from a shared library.

## Required native-library contract

The Android port must produce one compatible `libqemu-system-<guest>.so` for each guest target that the app exposes, for the selected Android host ABI. The JNI bridge currently expects:

- `qemu_init` (with the legacy `main` fallback)
- `qemu_main_loop`
- `qemu_cleanup`
- `limbo_sdl_scale_hint`
- `limbo_vga_full_update`
- `limbo_ignore_breakpoint_invalidate`
- `gui_refresh_interval_default`
- `gui_refresh_interval_idle`
- VNC refresh-rate globals

The current QEMU 5.1.0 patch supplies or modifies several Limbo-specific symbols and Android compatibility behaviors. These must be ported and verified against QEMU 11 rather than assumed to exist upstream.

## APK integration gates

1. Cross-compile QEMU 11.1.2 and its required libraries with the Android NDK for the intended host ABI.
2. Build a shared-library target (not just the upstream executable) and verify the required JNI symbols using the NDK's `llvm-nm`.
3. Port the Android compatibility and display/input changes from `qemu-5.1.0.patch` as a version-specific QEMU 11 patch.
4. Stage the shared libraries and QEMU 11 firmware/ROM/keymap assets into the existing Gradle modules.
5. Build all four APKs and inspect each APK's native libraries and assets.
6. Run device/emulator smoke tests for guest boot, storage, networking, display/input, shutdown and pause/resume.

## Safety rule

Do not change the production Android workflow's QEMU version until these gates pass. A successful Linux upstream build or an APK built against QEMU 5.1.0 is not evidence that QEMU 11 is working in Limbo.
