# seL4 SDK

The seL4 SDK provides system developers with the core components required to create an seL4 based system.

The SDK is structured by *platform* and *configuration*.

A *platform* is a specific hardware target supported by the seL4 SDK.
Each *platform* supports one or more *configurations*.

In the SDK there is a directory for each platform / configuration combination: `$platform/$configuration`.
Under each of these directories the following files / directories are available:

* `bin/kernel.elf`: The kernel binary.
* `lib/libsel4.a`: Library archive for *libsel4*.
* `include`: C header files for *libsel4*.

A system developer can create applications (including an appropriate OS personality root server) by using the *libsel4* C ABI bindings.

## What's not in SDK?

The goal of the SDK is to maximise the flexibility available to a system developer when it comes to integrating seL4 into a larger system.

As such there are a lot of things that are *not* included in the SDK.

The SDK **does not** provide a build system.
There are no plans to provide a build system as part of the SDK.
Note: The SDK itself is, currently, built using a combination of cmake, ninja and custom Python build scripts. These tools are *not* made available as part of the SDK, and there is no need for a system developer to use cmake or any other tool used internally.

The SDK **does not** provide a C library or C runtime.
There are currently no plans to provide a C library or C runtime as part of the SDK.

The SDK **does not** provide tools for loading and initialising the kernel on hardware.
There *are* plans for to provide such tooling as part of the SDK in future releases.

The SDK **does not** provide bindings to languages other than C.
Although there are currently no plans to offer other language bindings, external contributions to provide alternative bindings are welcomed.

## How do I use it?

The SDK is designed to be used directly by developers who are creating their own seL4 based operating system personality.
Creating an operating system from scratch, even while leveraging a microkernel, is a lot of work!
Depending on your requirements it may be more appropriate to build your system based on existing operating systems personalities.

The starting point to making a system that uses seL4 is to build an appropriate root server.
This will generally be a C application that links against libsel4.
Assuming `gcc` is used, `libsel4` can be used by passing an appropriate `-I`, `-L` and `-l` options on the command line.

For example, assumes the environment variable `$SDK` contains the path to your SDK, and you are building against the *default* configuration for *pc99* then an appropriate command would be:

    gcc -I$SDK/pc99/default/include -L$SDK/pc99/default/lib -lsel4 <yourfile.c>

Note: This is not intended to be a complete example! You will likely need to pass other flags such as `-ffreestanding`.

## How do I make a bootable image?

It is the responsibility of the OS personality developer to handle the loading of the kernel image into memory and appropriately boot-strapping the hardware.

This generally means writing some code that runs on the hardware prior to the kernel running.

Currently this is left as an exercise for the reader!
The next version of this documentation shall describe in more detail the exact loading requirements.

Note: Future versions of the SDK are intended to provide (optional) tools and default loaders that make this step easier!
