# QEMU 11.1.2 Android integration contract

## Why the Linux smoke test is not an APK build

The Linux smoke test proves that upstream QEMU 11.1.2 configures and builds its standalone emulator executables. Limbo does not launch those executables as subprocesses. Its JNI bridge uses `dlopen()` and resolves QEMU entry points and Limbo-specific globals from a shared library.

## Required native-library contract

The Android port must produce one compatible `libqemu-system-<guest>.so` for each guest target that the app exposes, for the selected Android host ABI. The JNI bridge expects the following symbols. The QEMU 11 branch now also updates the bridge's function-pointer signatures to call `qemu_init(argc, argv)`, capture the `qemu_main_loop()` status, and pass it to `qemu_cleanup(status)`, while retaining the legacy `main` fallback:

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

1. Cross-compile QEMU 11.1.2 and its required libraries with the Android NDK for the intended host ABI. QEMU 11 requires an updated GLib/Pixman/SDL dependency strategy; the current QEMU 5.1 dependency pins are not assumed compatible.
2. Adapt the QEMU 11 Meson target to emit a Limbo-loadable shared library (not just the upstream executable) and verify the required JNI symbols using the NDK's `llvm-nm`.
3. Port the Android compatibility and display/input changes from `qemu-5.1.0.patch` as a version-specific QEMU 11 patch.
4. Stage the shared libraries and QEMU 11 firmware/ROM/keymap assets into the existing Gradle modules.
5. Build all four APKs and inspect each APK's native libraries and assets.
6. Run device/emulator smoke tests for guest boot, storage, networking, display/input, shutdown and pause/resume.

## Safety rule

Do not change the production Android workflow's QEMU version until these gates pass. A successful Linux upstream build or an APK built against QEMU 5.1.0 is not evidence that QEMU 11 is working in Limbo.

## Ported Android-specific changes (QEMU 11.1.2)

The version-specific source patcher is `scripts/patch-qemu-11-limbo-android.py`. It applies guarded edits to QEMU 11.1.2 for:

- JNI-adjustable SDL refresh intervals and VNC refresh intervals.
- A full VGA refresh request triggered by Limbo's existing JNI variable.
- SDL renderer selection (software/hardware), render scaling hint, and guest-resolution callback.
- A null-console guard around SDL pointer events.
- Android VNC keyboard punctuation that requires synthesized Shift events.
- Android audio default frequency (22.05 kHz).
- Android mmap constants and a KVM error message that avoids glibc's `%m` format extension.

The CI workflow now applies this patcher before compiling the experimental shared-library target with `__LIMBO__` enabled. This is an early Linux-host integration check; the Android-only VNC and Bionic code paths still require an NDK cross-build.

## Known patch items not yet ported or proven

- The QEMU 5.1 breakpoint-invalidation hook has no confirmed one-to-one equivalent in the QEMU 11 source layout. The JNI variable is not yet implemented for QEMU 11; do not rely on that tuning option until it is ported deliberately.
- The old monitor file-descriptor workaround and the old configure-time feature overrides were not copied blindly because QEMU 11 moved to Meson and changed those subsystems. Each must be checked against the actual Android NDK/API level during cross-compilation.
- SDL display behavior, VNC keyboard mapping, audio, and KVM diagnostics have not yet been validated on a physical Android device.
