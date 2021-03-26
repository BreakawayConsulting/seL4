#pragma once

#ifdef HAVE_AUTOCONF
#include <autoconf.h>
#endif

#define seL4_NumHWBreakpoints (6)
#define seL4_NumExclusiveBreakpoints (6)
#define seL4_NumExclusiveWatchpoints (4)
#ifdef CONFIG_HARDWARE_DEBUG_API
#define seL4_FirstWatchpoint (6)
#define seL4_NumDualFunctionMonitors (0)
#endif

#if CONFIG_WORD_SIZE == 32
#error "Unsupported word size"
#endif

