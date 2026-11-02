# Hardware compatibility

The first supported target is modern x86-64 laptops. Profiles are a resource
selection policy, not a claim that every device or accelerator has been
physically validated.

| Profile | Typical RAM | Initial AI behavior |
|---|---:|---|
| Minimal | 4–8 GiB | Offline references; optional smallest CPU model if runtime check passes |
| Lightweight | 8–16 GiB | Small quantized CPU or supported GPU model |
| Standard | 16–32 GiB | Mid-size quantized model selected from verified payload |
| Accelerated | 32–64 GiB | Prefer tested NVIDIA/AMD/Intel backend and compatible model |
| High Performance | 64+ GiB | Highest-priority bundled model fitting usable RAM/VRAM |

The selector reserves memory for the OS and other applications, never assumes
that shared graphics memory is dedicated VRAM, and falls back to CPU when an
accelerator is unsupported or not verified. NVIDIA Secure Boot signing,
proprietary driver availability, and AMD/Intel backend support are validated
per image and are not promised generically. GPS, battery, and storage facts are
reported when the kernel exposes them.

Test hardware fixtures are synthetic. Actual validation in the current build
environment is limited to the workstation used for ISO construction; physical
field laptops remain untested until a separate acceptance report names them.
