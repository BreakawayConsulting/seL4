#
# SPDX-License-Identifier: GPL-2.0-only
#

cmake_minimum_required(VERSION 3.7.2)

declare_platform(tqma8xqp KernelPlatformTqma8xqp PLAT_TQMA8XQP KernelArchARM)

if(KernelPlatformTqma8xqp)
    declare_seL4_arch(aarch64)
    set(KernelArmCortexA35 ON)
    set(KernelArchArmV8a ON)
    config_set(KernelARMPlatform ARM_PLAT ${KernelPlatform})
    set(KernelArmVtimerUpdateVOffset OFF)
    list(APPEND KernelDTSList "tools/dts/${KernelPlatform}.dts")
    list(APPEND KernelDTSList "src/plat/tqma8xqp/overlay-${KernelPlatform}.dts")
    declare_default_headers(
        TIMER_FREQUENCY 8000000llu
        MAX_IRQ 512
        TIMER drivers/timer/arm_generic.h
        INTERRUPT_CONTROLLER arch/machine/gic_v3.h
        NUM_PPI 32
        CLK_MAGIC 1llu
        CLK_SHIFT 3u
        KERNEL_WCET 10u
    )
endif()

add_sources(
    DEP "KernelPlatformTqma8xqp"
    CFILES src/arch/arm/machine/gic_v3.c src/arch/arm/machine/l2c_nop.c
)
