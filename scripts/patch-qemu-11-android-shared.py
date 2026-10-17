#!/usr/bin/env python3
"""Apply the narrow QEMU 11.1.2 Meson change needed to build a Limbo .so.

This deliberately keeps upstream executable targets intact and adds a parallel
shared-library target. It is a build-system experiment, not a complete Android
compatibility patch.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
options = root / "meson_options.txt"
meson = root / "meson.build"

opt_text = options.read_text()
option_line = "option('limbo_android_shared_library', type: 'boolean', value: false,\n       description: 'build additional Limbo-loadable system emulator shared libraries')\n"
if "limbo_android_shared_library" not in opt_text:
    options.write_text(opt_text.rstrip() + "\n\n" + option_line)

text = meson.read_text()
needle = """    emulator = executable(exe_name, exe['sources'],
               install: true,
               c_args: c_args,
               dependencies: arch_deps + exe['dependencies'],
               objects: lib.extract_all_objects(recursive: true),
               link_depends: [block_syms, qemu_syms],
               link_args: link_args,
               win_subsystem: exe['win_subsystem'])
"""
addition = needle + """
    # Limbo loads QEMU in-process with dlopen() rather than spawning a
    # qemu-system process. Keep the normal executable for developer tools and
    # CI, and optionally build a parallel shared object for the Android port.
    if get_option('limbo_android_shared_library') and target.endswith('-softmmu')
      limbo_emulator = shared_library('qemu-system-' + target_name,
               exe['sources'],
               install: true,
               c_args: c_args,
               dependencies: arch_deps + exe['dependencies'],
               objects: lib.extract_all_objects(recursive: true),
               link_depends: [block_syms, qemu_syms],
               link_args: link_args,
               gnu_symbol_visibility: 'default',
               name_prefix: 'lib')
      emulators += {exe['name'] + '-limbo-shared': limbo_emulator}
    endif
"""
if "limbo_android_shared_library" not in text:
    if needle not in text:
        raise SystemExit("ERROR: expected QEMU 11.1.2 emulator target block not found; refusing to patch")
    meson.write_text(text.replace(needle, addition, 1))
elif "limbo_emulator = shared_library" not in text:
    raise SystemExit("ERROR: option exists but shared-library target block is missing")
print("QEMU Limbo shared-library target patch applied")
