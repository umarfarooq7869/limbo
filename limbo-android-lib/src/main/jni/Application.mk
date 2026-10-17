LIMBO_JNI_ROOT := $(CURDIR)/jni

include $(LIMBO_JNI_ROOT)/android-limbo-build.mak

#Suppress Format errors from logutils.h macros
APP_CFLAGS += -Wno-format-security

# QEMU 11 changed qemu_init/qemu_main_loop/qemu_cleanup signatures.
# This define is enabled only by the QEMU 11 Android build path.
ifeq ($(USE_QEMU_VERSION),11.1.2)
    APP_CFLAGS += -DLIMBO_QEMU_11
endif

#Debug/Release
ifeq ($(NDK_DEBUG),1)
    APP_OPTIM := debug
else
    APP_OPTIM := release
endif

#Don't remove this
APP_CFLAGS += -include $(LOGUTILS)
APP_LDFLAGS += -llog
ifeq ($(USE_GCC),true)
	APP_CFLAGS +=-std=gnu99
endif

APP_ARM_MODE=$(ARM_MODE)

$(info NDK_TOOLCHAIN_VERSION = $(NDK_TOOLCHAIN_VERSION))
$(info NDK_DEBUG = $(NDK_DEBUG))
$(info APP_ARM_MODE = $(APP_ARM_MODE))
$(info APP_ARM_NEON = $(APP_ARM_NEON))
$(info APP_OPTIM = $(APP_OPTIM))
$(info APP_ABI = $(APP_ABI))
$(info APP_PLATFORM = $(APP_PLATFORM))
$(info NDK_PROJECT_PATH = $(NDK_PROJECT_PATH))
$(info ARCH_CFLAGS = $(ARCH_CFLAGS))
$(info APP_CFLAGS = $(APP_CFLAGS))
