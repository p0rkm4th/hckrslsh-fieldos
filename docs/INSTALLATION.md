# Installation

The release target is an offline-capable USB installer for x86-64 laptops.
The installation flow must let the owner select the target disk, create a
user/password, optionally enable full-disk encryption, and confirm any disk
erase. Provisioning reads its package and content payload from the installer
media and must not rely on network access.

For development, boot the ISO only in QEMU/KVM with a disposable qcow2 disk.
Never point the automated smoke test at a host block device. Until the test
ISO passes end-to-end acceptance, use the official Ubuntu installer for normal
machines and treat FieldOS artifacts as experimental.

After first boot, the desktop launcher opens the local N.O.M.A.D. interface.
Services start automatically. The diagnostic command reports selected
hardware profile, model, local service health, available storage, and missing
optional devices. Software updates and additional content packs are explicit
owner-initiated actions and may require an internet-connected session.
