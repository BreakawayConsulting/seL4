#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: GPL-2.0-only
#

add_sources(
    DEP "KernelArchArmV6"
    PREFIX src/arch/arm/armv/armv6
    CFILES cache.c user_access.c
    ASMFILES machine_asm.S
)
