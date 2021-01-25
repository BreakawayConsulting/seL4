<!--
     Copyright 2021, Breakaway Consulting Pty. Ltd.

     SPDX-License-Identifier: GPL-2.0-only
-->

# seL4 build instructions

seL4 is distributed as either *source* a a pre-built [SDK](sdk.md).

If you are simply *using* seL4, it is recommended that you use a pre-built SDK.
However, there are cases when you may which to build the SDK yourself:

* Adding support for a new platform.
* Adding support for a new configuration.
* Ensuring traceability from SDK to source.
* Developing new features for the kernel.
* Fixing a bug.

This document attempts to describe exactly how the build system works.

Unfortunately the build system has *evolved* over time and is consequently relatively complex!

## Overview

This section provides and overview of the build and describes the main tools involved in the build system.
Later sections go into each tool in more detail.

The overall build is performed iteratively over each supported platform / configuration combination.
(See the [SDK](sdk.md) doc more details on platforms and configurations).

The following steps are perform for each platform / configuration combination:

Build script set up (using `cmake`) is generated into a unique build directory (`build/$platform/$configuration`).
The build tool `ninja` is then invoked to actually run the build tools (generating headers, compiling and linking etc).
FInally, the appropriate build outputs are copied from `build/$platform/$configuration` into `sdk/$platform/$configuration`.

This overall process is performed by the `build.py` script.

## build.py

`build.py` lists platforms, and their supported configurations, in the `PLATFORMS` variable.
This variable should be updated to add (or change) existing configurations to a platform.

A configuration is a dictionary of CMake variables that are passed to CMake when the build script is generated.

`build.py` can be passed either the `--all` option, which will try to build all possible configurations.
Alternatively, `--platform` can be passed to build all configurations for a specific platform.
Finally `--configuration` can be combined with `--platform` to only build a specific configuration.

When `build.py` is invoked it calls `cmake` and `ninja` appropriately.
This will use standard `ninja` rules to only re-run the necessary commands required when rebuilding.
Optionally, `--force` can be passed which will make `build.py` delete and recreate the build directory to ensure a full build.
Although in a perfect world this would be unnecessary it can be the case that changes to certain files does not correctly cause commands to be re-run by the build system.

## CMake

[CMake](https://cmake.org/) is a software configuration tool which generates a build script based on input variables.

Within the scope of the seL4 build system it is invoked by `build.py` with a set of specified variables, and then generate a `build.ninja` file which controls the actual build.

From a historical point of view CMake previously formed to main build system for seL4, however it is limited to a single configuration at any point in time.
As it was not easily possible to migrate the CMake based build system itself to support multiple concurrent configurations it is now invoked multiple times (from `build.py`) for each individual configuration.

The main *entry point* to the CMake system is the `CMakeLists.txt` file in the root directory.
This imports the `configs/seL4Config.cmake` file to configure all the internal build variables based on the variables passed on the command line.
The `kernel/CMakeLists.txt` and `libsel4/CMakeLists.txt` then create the rules required to build the various files.

Part of the configuration that *CMake* performs is the generation of autoconf like headers that make the various configuartion options avaialble to the kernel and libsel4 source code.

## Ninja

Ninja does not perform any configuration.
Ninja simply takes the `build.ninja` file that is generated as part of the CMake process and then executes the commands as necessary.

