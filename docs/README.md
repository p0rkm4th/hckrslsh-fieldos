# Documentation guide

Use this page to find the right FieldOS documentation for each task.

| Document | Purpose |
|---|---|
| [Architecture](ARCHITECTURE.md) | Components, boot provisioning, network boundaries, and data paths |
| [Installation](INSTALLATION.md) | Customer installation and post-install checks |
| [Operations](OPERATIONS.md) | Firstboot troubleshooting, diagnostics, and persistent data |
| [Hardware](HARDWARE.md) | Hardware detection, model selection, and validation limits |
| [Offline content](OFFLINE-CONTENT.md) | Payload inventory, attribution, and redistribution review |
| [Redistribution review](REDISTRIBUTION.md) | Artifact-level licensing evidence and open release clearance actions |
| [Container images](CONTAINER-IMAGES.md) | Pinned service image identities and upstream direct-license references |
| [Content packs](CONTENT-PACKS.md) | Pack manifests, deterministic archives, safe installation, planned categories, and integration limits |
| [Security](SECURITY.md) | Docker privileges, local ports, secrets, and network boundaries |
| [Testing](TESTING.md) | Unit and disposable VM acceptance tests, artifacts, cleanup |
| [Release](RELEASE.md) | Measured release status, evidence, and release gates |
| [FieldOS Lab](FIELDOS-LAB.md) | Kasm workspace operation, network boundary, snapshot recovery, and current verification limits |

The repository root README is the project overview and command entry point.
Release readiness is determined by the evidence in `RELEASE.md`, not by the
presence of a built ISO.
