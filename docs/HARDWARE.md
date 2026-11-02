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

The detector reports free NVIDIA VRAM from `nvidia-smi` and available
dedicated DRM VRAM where the kernel exposes `mem_info_vram_total` and
`mem_info_vram_used`. It does not count shared system memory as dedicated
VRAM. The selector reserves memory for the OS and other applications and
falls back to CPU when an accelerator is unsupported or not verified. NVIDIA Secure Boot signing,
proprietary driver availability, and AMD/Intel backend support are validated
per image and are not promised generically. GPS, battery, and storage facts are
reported when the kernel exposes them.

The operator may set `/etc/fieldos/model-override` before firstboot to request a
bundled model by manifest ID. The selector still rejects a model absent from
the payload or above the detected memory budget. The default firstboot path
marks only CPU as validated; GPU configuration is not enabled just because a
GPU appears in the detector output.

Fixture tests cover memory bands, model fallback, available payload IDs, manual
override validation, CPU features, and available VRAM calculation. These are
synthetic selection tests. They do not validate GPU inference. Hardware used
by the current QEMU acceptance test is virtual CPU only; physical field
laptops and accelerators still need separate test evidence.
