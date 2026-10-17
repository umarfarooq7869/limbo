#!/usr/bin/env python3
"""Port the QEMU 5.1 Limbo UI/runtime hooks onto QEMU 11.1.2 source.

Only applies version-specific, marker-guarded changes. It aborts if upstream
source anchors drift, rather than silently producing a partially patched tree.
Run against a clean qemu-11.1.2 source directory.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
changes = []

def edit(rel, old, new, label, count=1):
    p = root / rel
    text = p.read_text()
    if label in text:
        return
    found = text.count(old)
    if found != count:
        raise SystemExit(f"{rel}: expected {count} anchor(s) for {label}, found {found}; no safe automatic patch")
    p.write_text(text.replace(old, new, count))
    changes.append(label)

# Runtime-adjustable refresh rates used by the existing JNI layer.
edit("include/ui/console.h",
"""/* in ms */
#define GUI_REFRESH_INTERVAL_DEFAULT    30
#define GUI_REFRESH_INTERVAL_IDLE     3000
""",
"""/* in ms */
#ifdef __LIMBO__
extern int gui_refresh_interval_default;
extern int gui_refresh_interval_idle;
#define GUI_REFRESH_INTERVAL_DEFAULT gui_refresh_interval_default
#define GUI_REFRESH_INTERVAL_IDLE    gui_refresh_interval_idle
#else
#define GUI_REFRESH_INTERVAL_DEFAULT    30
#define GUI_REFRESH_INTERVAL_IDLE     3000
#endif
""", "runtime-refresh-header")

edit("ui/console.c",
"""static DisplayState *display_state;
""",
"""#ifdef __LIMBO__
int gui_refresh_interval_default = 30;
int gui_refresh_interval_idle = 300;
#endif

static DisplayState *display_state;
""", "runtime-refresh-globals")

# VGA full refresh trigger used when Android changes scale/viewport.
edit("hw/display/vga.c",
"""bool have_vga = true;
""",
"""bool have_vga = true;

#ifdef __LIMBO__
int limbo_vga_full_update;
#endif
""", "vga-refresh-global")
edit("hw/display/vga.c",
"""        if (full_update) {
            update = 1;
""",
"""#ifdef __LIMBO__
        if (full_update || limbo_vga_full_update) {
#else
        if (full_update) {
#endif
            update = 1;
""", "vga-force-full-update")
edit("hw/display/vga.c",
"""    g_free(snap);
    memset(s->invalidated_y_table, 0, sizeof(s->invalidated_y_table));
}

static void vga_draw_blank""",
"""#ifdef __LIMBO__
    limbo_vga_full_update = 0;
#endif
    g_free(snap);
    memset(s->invalidated_y_table, 0, sizeof(s->invalidated_y_table));
}

static void vga_draw_blank""", "vga-refresh-reset")

# SDL renderer selection and scale-quality hint for Android.
edit("ui/sdl2.c",
"""        /* The SDL renderer is only used by sdl2-2D, when OpenGL is disabled */
        scon->real_renderer = SDL_CreateRenderer(scon->real_window, -1, 0);
""",
"""        /* The SDL renderer is only used by sdl2-2D, when OpenGL is disabled */
#if defined(__LIMBO_SDL_FORCE_SOFTWARE_RENDERING__)
        scon->real_renderer = SDL_CreateRenderer(scon->real_window, -1, SDL_RENDERER_SOFTWARE);
#elif defined(__LIMBO_SDL_FORCE_HARDWARE_RENDERING__)
        scon->real_renderer = SDL_CreateRenderer(scon->real_window, -1, SDL_RENDERER_ACCELERATED);
#else
        scon->real_renderer = SDL_CreateRenderer(scon->real_window, -1, 0);
#endif
""", "sdl-renderer-selection")
edit("ui/sdl2.c",
"""static int sdl2_num_outputs;
""",
"""#ifdef __LIMBO__
int limbo_sdl_scale_hint = -1;
#endif

static int sdl2_num_outputs;
""", "sdl-scale-global")
edit("ui/sdl2.c",
"""    if (SDL_GetHintBoolean("QEMU_ENABLE_SDL_LOGGING", SDL_FALSE)) {
        SDL_LogSetAllPriority(SDL_LOG_PRIORITY_VERBOSE);
    }
""",
"""#ifdef __LIMBO__
    if (limbo_sdl_scale_hint == 1) {
        SDL_bool hint_ok = SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "1");
        qemu_log("Limbo: SDL scale-quality hint=%d result=%d\\n", limbo_sdl_scale_hint, hint_ok);
    }
#endif
    if (SDL_GetHintBoolean("QEMU_ENABLE_SDL_LOGGING", SDL_FALSE)) {
        SDL_LogSetAllPriority(SDL_LOG_PRIORITY_VERBOSE);
    }
""", "sdl-scale-quality-hint")

# Notify Java of guest resolution changes through the project's existing JNI hook.
edit("ui/sdl2-2d.c",
"""    sdl2_2d_redraw(scon);
}

void sdl2_2d_refresh""",
"""    sdl2_2d_redraw(scon);
#ifdef __LIMBO__
    Android_JNI_SetVMResolution(surface_width(new_surface), surface_height(new_surface));
#endif
}

void sdl2_2d_refresh""", "sdl-resolution-callback")

# VNC refresh controls are accessed by JNI by symbol name.
edit("ui/vnc.c",
"""#define VNC_REFRESH_INTERVAL_BASE GUI_REFRESH_INTERVAL_DEFAULT
#define VNC_REFRESH_INTERVAL_INC  50
#define VNC_REFRESH_INTERVAL_MAX  GUI_REFRESH_INTERVAL_IDLE
""",
"""#ifdef __LIMBO__
int vnc_refresh_interval_base = 30;
int vnc_refresh_interval_inc = 30;
#define VNC_REFRESH_INTERVAL_BASE vnc_refresh_interval_base
#define VNC_REFRESH_INTERVAL_INC  vnc_refresh_interval_inc
#else
#define VNC_REFRESH_INTERVAL_BASE GUI_REFRESH_INTERVAL_DEFAULT
#define VNC_REFRESH_INTERVAL_INC  50
#endif
#define VNC_REFRESH_INTERVAL_MAX  GUI_REFRESH_INTERVAL_IDLE
""", "vnc-refresh-controls")

# Android audio default chosen by the original Limbo integration.
edit("audio/audio.c",
"""    if (!pdo->has_frequency) {
        pdo->has_frequency = true;
        pdo->frequency = 44100;
    }
""",
"""    if (!pdo->has_frequency) {
        pdo->has_frequency = true;
#ifdef __LIMBO__
        pdo->frequency = 22050;
#else
        pdo->frequency = 44100;
#endif
    }
""", "android-audio-default")

print("Applied QEMU 11 Limbo patches: " + ", ".join(changes))
print(f"Patch markers present: {len(changes)}")
