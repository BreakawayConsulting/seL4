import sys
from contextlib import contextmanager
from pathlib import Path
from shutil import copy as copy_file, copytree, rmtree
from os import system, chdir

PLATFORMS = [
    # "ariane",
    # "hifive",
    # "polarfire",
    # "rocketchip",
    # "spike",
    "allwinnerA20",
    "am335x",
    "apq8064",
    "bcm2837",
    "exynos4",
    "exynos5",
    "hikey",
    "imx31",
    "imx6",
    "imx7",
    "omap3",
    "tk1",
    "zynq7000",
    "fvp",
    "imx8mm-evk",
    "imx8mq-evk",
    "odroidc2",
    "rockpro64",
    "tx1",
    "tx2",
    "zynqmp",
    "pc99",
]

SOURCE_PATH = Path(".")
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
    sdk_dir.mkdir()

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


def build_one(platform):
    print(f"Compiling for platform: {platform}")
    build_script = (Path.cwd() / "setup-build.sh").resolve()
    build_dir = BUILD_PATH / platform
    build_dir.mkdir(exist_ok=True)
    with cwd(build_dir):
        cmd = f"{build_script} -DKernelPlatform={platform}"
        print(f"Running: {build_script}")
        r = system(cmd)
        if r != 0:
            print(f"Error running command: {cmd}")
            return 1
        r = system("ninja kernel.elf libsel4.a")
        if r != 0:
            print("Error building")
            return 1

    sdk_dir = SDK_PATH / platform
    generate_sdk_directory(build_dir, sdk_dir)


def main():
    BUILD_PATH.mkdir(exist_ok=True)
    SDK_PATH.mkdir(exist_ok=True)

    for platform in PLATFORMS:
        build_one(platform)

if __name__ == "__main__":
    sys.exit(main())