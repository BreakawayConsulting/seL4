import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path
from shutil import copy as copy_file, copytree, rmtree
from os import system, chdir

PLATFORMS = {
    # x86
    "pc99" : {
        "debug": {
            "KernelDebugBuild": True,
            "KernelPrinting": True,
            "KernelVerificationBuild": False
        }
    },

    # RISC-V
    # "ariane": {"default": {}},
    # "hifive": {"default": {}},
    # "polarfire": {"default": {}},
    # "rocketchip": {"default": {}},
    # "spike": {"default": {}},

    # ARM
    "allwinnerA20": {"default": {}},
    "am335x": {"default": {}},
    "apq8064": {"default": {}},
    "bcm2837": {"default": {}},
    "exynos4": {"default": {}},
    "exynos5": {"default": {}},
    "hikey": {"default": {}},
    "imx31": {"default": {}},
    "imx6": {"default": {}},
    "imx7": {"default": {}},
    "omap3": {"default": {}},
    "tk1": {"default": {}},
    "zynq7000": {"default": {}},
    "fvp": {"default": {}},
    "imx8mm-evk": {"default": {}},
    "imx8mq-evk": {"default": {}},
    "odroidc2": {"default": {}},
    "rockpro64": {"default": {}},
    "tx1": {"default": {}},
    "tx2": {"default": {}},
    "zynqmp": {"default": {}},
    "tqma8xqp": {
        "default": {},
        "debug": {
            "KernelDebugBuild": True,
            "KernelPrinting": True,
            "KernelVerificationBuild": False
        }
    },
    "ipq8074" : {
        "default": {},
        "debug": {
            "KernelDebugBuild": True,
            "KernelPrinting": True,
            "KernelVerificationBuild": False
        }
    },
}

PLATFORM_CHOICES = list(sorted(PLATFORMS.keys()))
CONFIGURATION_CHOICES = list(sorted(set.union(*(set(v.keys()) for v in PLATFORMS.values()))))

SOURCE_PATH = Path(".").resolve()
BUILD_PATH = Path("build")
SDK_PATH = Path("sdk")

def parse_cmake_cache(cache_path):
    """Parse the cmake cache and return all the variables as a dictionary."""
    vals = {}
    with cache_path.open() as f:
        for line_idx, l in enumerate(f.readlines(), 1):
            l = l.strip()
            if len(l) == 0:
                continue
            if l.startswith("#"):
                continue
            if l.startswith("//"):
                continue
            name, raw_value = l.split(":", 1)
            value_type, val_raw = raw_value.split("=", 1)
            if value_type == "STRING":
                val = val_raw
            elif value_type == "STATIC": # Constant
                val = val_raw
            elif value_type == "INTERNAL": # Not in the GUI
                val = val_raw
            elif value_type == "FILEPATH": # Path to file
                val = Path(val_raw)
            elif value_type == "PATH": # Path to directory
                val = Path(val_raw)
            elif value_type == "BOOL":
                val = {
                    "ON": True,
                    "OFF": False,
                    "NO": False,
                    "FALSE": False,
                    "": None,
                }[val_raw]
            else:
                raise Exception(f"Invalid value type: {value_type} ({cache_path}:{line_idx})")

            vals[name] = val
    return vals


@contextmanager
def cwd(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    chdir(path)
    try:
        yield
    finally:
        chdir(prev_cwd)


def generate_sdk_directory(build_dir, sdk_dir):
    """From a given build directory create an SDK directory"""
    cache_file = build_dir / "CMakeCache.txt"
    cmake_vars = parse_cmake_cache(cache_file)

    if sdk_dir.exists():
        rmtree(sdk_dir)
    sdk_dir.mkdir(parents=True)

    bin_dir = sdk_dir / "bin"
    lib_dir = sdk_dir / "lib"
    include_dir = sdk_dir / "include"

    # Populate bin directory with the kernel ELF file
    bin_dir.mkdir()
    kernel_path = build_dir / "kernel" / "kernel.elf"
    copy_file(kernel_path, bin_dir)

    # Populate lib directory with libsel4.a
    lib_dir.mkdir()
    copy_file(build_dir / "libsel4" / "libsel4.a", lib_dir)

    # Populate the include directory.
    # This combines files directly from the source directory with
    # generated header files
    include_dir.mkdir()
    include_sel4 = include_dir / "sel4"
    include_kernel = include_dir / "kernel"
    include_interfaces = include_dir / "interfaces"

    base = (SOURCE_PATH / "libsel4" / "include" / "sel4")
    copytree(base, include_sel4)

    for cmake_var, base_dir, leaf_dir in [
        ("KernelArch", "arch_include", "arch"),
        ("KernelSel4Arch", "sel4_arch_include", "sel4_arch"),
        ("KernelPlatform", "sel4_plat_include", "plat"),
        ("KernelWordSize", "mode_include", "mode"),
    ]:
        base = (SOURCE_PATH / "libsel4" / base_dir / cmake_vars[cmake_var] / "sel4" / leaf_dir)
        copytree(base, include_sel4 / leaf_dir)

    # Manually copy generated files
    copy_file(build_dir / "libsel4" / "autoconf" / "autoconf.h", include_dir)
    sel4_gen_dir = build_dir / "libsel4" / "include" / "sel4"
    copy_file(sel4_gen_dir / "syscall.h", include_sel4)
    copy_file(sel4_gen_dir / "shared_types_gen.h", include_sel4)
    copy_file(sel4_gen_dir / "invocation.h", include_sel4)

    copy_file(build_dir / "libsel4" / "gen_config" / "sel4" / "gen_config.h", include_sel4)
    arch_dir = build_dir / "libsel4" / "arch_include" / cmake_vars["KernelArch"] / "sel4" / "arch"
    copy_file(arch_dir / "invocation.h", include_sel4 / "arch")
    sel4_arch_dir = build_dir / "libsel4" / "sel4_arch_include" / cmake_vars["KernelSel4Arch"] / "sel4" / "sel4_arch"
    copy_file(sel4_arch_dir /  "types_gen.h", include_sel4 / "sel4_arch")
    copy_file(sel4_arch_dir /  "invocation.h", include_sel4 / "sel4_arch")

    include_interfaces.mkdir()
    copy_file(build_dir / "libsel4" / "include" / "interfaces" / "sel4_client.h", include_interfaces)

    include_kernel.mkdir()
    copy_file(build_dir / "kernel" / "gen_config" / "kernel" / "gen_config.h", include_kernel)


def build(platform, configuration):
    build_dir = BUILD_PATH / platform / configuration
    build_dir.mkdir(parents=True, exist_ok=True)
    with cwd(build_dir):
        config_args = PLATFORMS[platform][configuration]
        config_strs = []
        for arg, val in sorted(config_args.items()):
            if isinstance(val, bool):
                str_val = "ON" if val else "OFF"
            else:
                str_val = str(val)
            s = f"-D{arg}={str_val}"
            config_strs.append(s)
        config_str = " ".join(config_strs)
        cmd = f"cmake -GNinja -DKernelPlatform={platform} {config_str} {SOURCE_PATH.absolute()}"
        print(f"Running: {cmd}")
        r = system(cmd)
        if r != 0:
            print(f"Error running command: {cmd}")
            return 1
        r = system("ninja kernel.elf libsel4.a")
        if r != 0:
            print("Error building")
            return 1

    sdk_dir = SDK_PATH / platform / configuration
    generate_sdk_directory(build_dir, sdk_dir)


def main():
    BUILD_PATH.mkdir(exist_ok=True)
    SDK_PATH.mkdir(exist_ok=True)

    parser = ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--platform", choices=PLATFORM_CHOICES)
    parser.add_argument("--configuration", choices=CONFIGURATION_CHOICES)
    args = parser.parse_args()
    builds = []
    if args.all:
        if args.platform is not None:
            parser.error("--platform must not be passed if --all is passed")
        if args.configuration is not None:
            parser.error("--configuration must not be passed if --all is passed")
        for platform, configs in PLATFORMS.items():
            for config in configs.keys():
                builds.append((platform, config))
    elif args.platform:
        if args.configuration is None:
            for config in PLATFORMS[args.platform].keys():
                builds.append((args.platform, config))
        elif args.configuration not in PLATFORMS[args.platform]:
            parser.error(f"configuration '{args.configuration}' not valid for platform '{args.platform}'")
        else:
            builds.append((args.platform, args.configuration))
    else:
        parser.error("Either --all or --platform must be specified")

    for platform, configuration in builds:
        build(platform, configuration)

if __name__ == "__main__":
    sys.exit(main())
