# Hardware compatibility

The first supported target is modern x86-64 laptops. Profiles are a resource
selection policy, not a claim that every device or accelerator has been
physically validated.

| Profile | Typical RAM | Initial AI behavior |
|---|---:|---|
| Minimal | 4–8 GiB | Offline references; smallest bundled CPU model when reserved memory allows and its smoke test passes |
| Lightweight | 8–16 GiB | Small quantized CPU or supported GPU model |
| Standard | 16–32 GiB | Mid-size quantized model selected from verified payload |
| Accelerated | 32–64 GiB | Prefer tested NVIDIA/AMD/Intel backend and compatible model |
| High Performance | 64+ GiB | Highest-priority bundled model fitting usable RAM/VRAM |

The detector reports CPU architecture and supported instruction flags,
logical and (when exposed by Linux) physical cores, total and currently
available RAM, candidate physical disks and root filesystem free space,
battery status, likely GPS device nodes, GPU
vendor/device IDs, detected driver, and available dedicated VRAM where exposed
by `nvidia-smi` or DRM sysfs. When `vulkaninfo` is installed, it also reports
each non-CPU Vulkan device's device-local memory budget; for integrated GPUs
this may be shared system memory. Vulkan budgets are runtime estimates, not
dedicated VRAM or proof of model capacity. GPU/driver facts do not prove
inference acceleration works. Available RAM is diagnostic; current model
selection still uses installed RAM minus its configured system reserve.

The selector requires the chosen backend to appear in each model's manifest.
That includes CPU fallback: a model that only lists GPU backends is not
selected for CPU even if its memory estimate fits. At startup, firstboot
validates the selected bundled model with a short generation request and tries
smaller compatible bundled models if loading or generation fails.

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
| GPU vendor/device and memory budget | Reports NVIDIA and DRM-visible GPUs; when `vulkaninfo` is present, reports Vulkan device-local budgets including shared memory on integrated GPUs; includes a GPU backend only after runtime validation | Driver/kernel compatibility, Secure Boot signing, container device access, runtime libraries, and physical inference tests must be added and validated |
| Model override | Tries the requested bundled model first, then smaller bundled models if its firstboot generation check fails | Operator must choose a bundled model that fits; a missing or too-large override is rejected |
| GPS hardware | Detects likely device nodes | Device protocol, permission model, local position service, map UI integration, and field testing are not implemented |

The measured acceptance VM was x86-64 with 12 GiB RAM, 6 virtual CPUs, an 80
GiB virtual disk, no virtual NIC, and no GPU. It is the only end-to-end
hardware profile tested so far. The initial physical support matrix is not
established; do not infer universal laptop compatibility from the QEMU run.

The operator may set `/etc/fieldos/model-override` before firstboot to request a
bundled model by manifest ID. The selector still rejects a model absent from
the payload or above the detected memory budget. If the requested model fits
but fails firstboot's generation smoke test, firstboot tries lower-parameter
bundled models that also fit. An invalid or over-budget override is rejected
instead of silently selecting another model. The default firstboot path marks
only CPU as validated; GPU configuration is not enabled just because a GPU
appears in the detector output.

The manual-override fallback behavior is a source change after the tested
`129da89` customer ISO. Its selector fixtures pass, but it has not yet been
included in a rebuilt ISO or exercised by firstboot on a VM.

After a model passes firstboot's local generation smoke test, FieldOS seeds
N.O.M.A.D.'s supported `chat.lastModel` preference from that model's Ollama
reference if the setting is absent, NULL, or empty. An existing nonempty value
is preserved. The firstboot unit is configured to block GNOME startup until
this preference is written, so the UI cannot save its initial default first;
this startup gate still needs fresh-VM validation.
N.O.M.A.D. continues to save a user's manual model selection through its
normal UI setting, and subsequent provisioning does not replace it. The source
change is committed but has not yet been included in an ISO or VM-validated.

The tested `8020fd3` candidate bundles Qwen3 1.7B Q4_K_M and 0.6B; firstboot
selected and validated 1.7B in the VM, while N.O.M.A.D.'s UI initially chose
0.6B. The source tree pins 1.7B as the preferred bundled candidate for
machines with enough memory and keeps 0.6B as fallback. An isolated CPU
comparison against the same handbook excerpt showed better exact date
extraction from 1.7B, but it did not exercise N.O.M.A.D.'s live retrieval, the
8 GiB install profile, or a customer installation. Evidence is in
`/mnt/shared/fieldos-model-eval-20261105/benchmark.json`; the candidate becomes
an accepted FieldOS model only after payload validation and a fresh offline
installation run.

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

## Hardware and runtime recheck — 2026-11-03

A fresh read-only detector run again found the i9-12900H, 62.46 GiB RAM,
NVIDIA RTX 3080 Ti Laptop GPU (16 GiB total, 15.57 GiB available), Intel
integrated graphics, NVMe storage, and battery. `nvidia-smi` reported driver
615.78.08. Docker lists only its standard `runc` runtimes; neither
`nvidia-container-runtime`, `nvidia-container-cli`, nor the NVIDIA Container
Toolkit package is installed. The selector therefore ran with only the CPU
backend marked validated and chose the bundled Qwen 0.6B model on CPU. No
FieldOS Ollama inference was run on the physical GPU. Evidence:
`/mnt/shared/fieldos-e2e/hardware-detection-20261103.json`,
`hardware-runtime-check-20261103.txt`, and
`hardware-selection-cpu-20261103.json`.

At source commit `6f11170b1334eb8339ea53f644480a912e0e5f1f`, the selector was
also run against IDs streamed from the actual prepared offline payload archive.
It found only the bundled Qwen 0.6B chat and Nomic Embed v1.5 models and chose
both with CPU when only CPU was marked validated, despite detecting the host's
NVIDIA and Intel GPUs. Evidence, including the hardware inventory, payload IDs,
and selection result:
`/mnt/shared/fieldos-e2e/hardware-selection-actual-payload-6f11170.json`. This
confirms inventory-based selection on this workstation; it does not load a
model, run inference, or validate GPU acceleration.

At source commit `d8fbc5588afcae3dec5db439059aa7424d5bd22b`, the detector used
the workstation's Vulkan memory reports to identify a 15.57 GiB NVIDIA
device-local budget and a 7.06 GiB Intel integrated-GPU budget. The CPU-only
selector still chose the bundled chat and embedding models. Evidence is
`/mnt/shared/fieldos-e2e/hardware-vulkan-d8fbc55.json`. This was host hardware
detection, not GPU inference. Later source revisions request `vulkan-tools` in
the offline APT payload, and current-source E2E provisioning passed. No
accelerated inference has been validated on a physical GPU.

## Physical detector recheck — 2026-11-05

A fresh read-only run of the current detector reported the same i9-12900H,
62.46 GiB RAM, RTX 3080 Ti Laptop GPU (16 GiB total, 15.57 GiB available),
Intel Iris Xe integrated GPU, and NVMe storage. Both GPU drivers were visible;
the detector correctly left `runtime_validated` false for each. The machine had
30.61 GiB available RAM and no likely GPS device. This is evidence that current
source detects this workstation's hardware, not that an installer selects or
uses GPU inference correctly. No inference was run. Full JSON evidence:
`/mnt/shared/fieldos-e2e/hardware-detection-20261105.json` (SHA-256
`f17a876dc84c93dd246703a8274a024090f672ff3cdc3cbe3ae9683e71b6b0d6`).
