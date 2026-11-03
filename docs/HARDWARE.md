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

The detector reports CPU architecture and supported instruction flags,
logical and (when exposed by Linux) physical cores, total and currently
available RAM, candidate physical disks and root filesystem free space,
battery status, likely GPS device nodes, GPU
vendor/device IDs, detected driver, and available dedicated VRAM where exposed
by `nvidia-smi` or DRM sysfs. It does not count shared system memory as
dedicated VRAM. It reports GPU/driver facts without treating them as proof
that inference acceleration works. Available RAM is diagnostic; current model
selection still uses installed RAM minus its configured system reserve.

The selector reserves memory for the OS, only considers model IDs present in
the offline payload, and checks model memory requirements. It requires an
explicitly runtime-validated backend plus a matching available driver before
choosing CUDA, ROCm, or Vulkan. VRAM from a different GPU vendor is not counted
for that backend. Firstboot currently validates CPU inference only and falls
back through smaller compatible bundled models if a generation smoke check
fails. NVIDIA Secure Boot signing, driver packages, and AMD/Intel runtime
support need per-device validation; they are not enabled generically. GPS,
battery, and storage facts are reported when the kernel exposes them.

## What adapts automatically and what needs support work

| Hardware characteristic | Automatic behavior | Manual work needed |
|---|---|---|
| CPU architecture/features and core count | Detects x86-64 and relevant instruction flags | New architecture/runtime support requires compatible Ubuntu packages, container images, and model formats |
| RAM and local storage | Reports installed/available RAM, physical disk capacity/type, and root filesystem free space; chooses a bundled model that fits installed RAM | The operator must choose an installation disk with sufficient capacity; a new payload tier/model needs its own manifest and bundle |
| GPU vendor/device and dedicated VRAM | Reports NVIDIA and DRM-visible GPUs; includes a GPU backend only after driver and runtime validation | Driver/kernel compatibility, Secure Boot signing, container device access, runtime libraries, and physical inference tests must be added and validated |
| Model override | Accepts `/etc/fieldos/model-override` only for a bundled model that fits | Operator is responsible for choosing a supported model ID |
| GPS hardware | Detects likely device nodes | Device protocol, permission model, local position service, map UI integration, and field testing are not implemented |

The measured acceptance VM was x86-64 with 12 GiB RAM, 6 virtual CPUs, an 80
GiB virtual disk, no virtual NIC, and no GPU. It is the only end-to-end
hardware profile tested so far. The initial physical support matrix is not
established; do not infer universal laptop compatibility from the QEMU run.

The operator may set `/etc/fieldos/model-override` before firstboot to request a
bundled model by manifest ID. The selector still rejects a model absent from
the payload or above the detected memory budget. The default firstboot path
marks only CPU as validated; GPU configuration is not enabled just because a
GPU appears in the detector output.

Fixture tests cover memory bands and available-memory detection, physical-core
counting, model fallback, available payload IDs, manual override validation,
mixed GPU vendors/VRAM matching, CPU features, and available VRAM calculation.
These are simulated hardware profiles. They do
not validate GPU inference. Hardware used by the current QEMU acceptance test
is virtual CPU only; physical field laptops and accelerators still need
separate test evidence.

## Physical development-workstation observation — 2026-11-02

A read-only detector run on the development laptop identified an Intel Core
i9-12900H, 62.46 GiB RAM, an NVIDIA GeForce RTX 3080 Ti Laptop GPU with a
16 GiB device-memory report and loaded NVIDIA 615.78.08 driver, an Intel
integrated GPU, NVMe storage, and a reported battery. `nvidia-smi` succeeded.
The Docker daemon exposes only its default runtime and the NVIDIA Container
Toolkit is absent, so Ollama container inference on this physical GPU was not
validated. This proves the host detector can observe this hardware; it does
not establish FieldOS GPU acceleration support or change the CPU-only firstboot
selection policy.
