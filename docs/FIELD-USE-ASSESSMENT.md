# Field-use assessment: disaster-preparedness scenarios

Date: 2026-11-04  
Assessment: **Not suitable as a standalone disaster-preparedness computer.**

This review checks the fresh customer desktop, bundled applications, offline content, and recorded guest tests. The candidate showed its FieldOS wallpaper and dock; Firefox visibly opened Kiwix and the Nashville map, and the source-library page responded. Start Here and Command Center shortcuts were visible but were not separately launched in this exact install. This is a content-coverage review, not a clinical, emergency-response, or field trial.

## Tested installation and interface

The current clean-source unattended test ISO at source `7e2674e285be158f56b556f048ad3c785d8b0cb9` passed a fresh no-NIC install, firstboot, local inference, embeddings, Kiwix, visible Middle Tennessee map rendering, all four core-pack activations/indexing, and two reboots. Report: `/mnt/shared/fieldos-e2e/20261104T152431Z-3714447/report.md`; test ISO SHA-256: `0fcb81e0f5e7043024486a6caa11ca31a7e85c2ae17054e4649c1d8f7b3c5fc6`.

The latest customer-mode ISO was built from clean source commit
`21ad4fcdb882998ca1c3bd47333b1139c162651c`:
`/mnt/shared/fieldos-releases/fieldos-customer-core4-21ad4fc.iso`, SHA-256
`38acf9bda9d62b328e5baf117895d25affa78688730cf9da1be7b4769791f9bd`. A fresh
interactive no-NIC install selected a disposable virtual disk and user, booted
the installed EFI disk, completed four-pack provisioning, and passed local AI,
embeddings, Kiwix search, visible Nashville zoom-13 rendering, and two reboots.
Evidence is in `/mnt/shared/fieldos-e2e/customer-core4-21ad4fc/report.md`. At
media handoff Ubuntu powered off after the remove-media prompt; a subsequent VM
power-on booted the installed disk without repair. Physical USB behavior is
untested.

The current customer image contains the four-pack core payload. Neither test VM
had a network adapter. These results do not test physical USB media handoff,
external weather alerts, physical GPS, or broad geographic coverage.

## Scenario walk-through

| Situation | What an offline user can actually use | Assessment |
|---|---|---|
| Power outage and food spoilage | One CDC source document, “Eat Safe Food After a Power Outage,” is bundled and linked from Start Here/Source Library. The tested AI safety guard refuses food-safety prompts. | **Narrow help available.** No broader food storage, cooking-fuel, or household power reference was verified. |
| Water service interruption | One CDC emergency-water PDF is bundled. It is available as a primary source; the AI guard refuses water-treatment questions. | **Narrow source available.** It does not cover every contaminant or local water advisory. Read the document directly; do not treat boiling as a universal treatment. |
| Tornado | A text-only NWS “What to Do During a Tornado” reference is bundled and indexed. The AI guard refuses tested tornado-shelter prompts. | **Basic source available.** No live alerts, local shelter database, or current warning feed works offline. |
| Hurricane or winter storm | Three NWS-derived FieldOS summaries in `us-weather-safety` 1.0.1 were installed and indexed from the core payload in both unattended and current interactive no-NIC tests. | **Source available.** No forecasts or alerts are provided. |
| Wildfire or evacuation | No dedicated wildfire source is bundled. The AI guard refused one tested wildfire prompt, but prior tests found alternate wording can bypass the keyword guard. | **Not dependable.** A refusal is not safety certification or evacuation guidance. |
| Flood | The FieldOS-edited NWS summary in `us-flood-safety` 1.0.0 was installed and indexed from the core payload in both unattended and current interactive no-NIC tests. | **Source available.** No current flood alerts, flood-zone data, or safe routing are provided. |
| Injury or medical emergency | No first-aid or trauma manual is bundled. The AI guard refused one severe-bleeding prompt. | **Not covered.** Do not rely on the AI for medical decisions. |
| Communications outage | No radio operation, emergency communications, or contact-plan reference was found in the bundled source set. | **Not covered.** |
| Travel, navigation, or loss of GPS | Firefox renders an interactive Middle Tennessee road map through zoom 13. Global and U.S. maps are overview-only through zoom 5. There is no verified GPS positioning, route calculation, trail data, or offline navigation. | **Useful local map viewer only.** It is useful only in the covered area and is not a navigation system. |
| Broad reference lookup | Kiwix opens and returns search results, but the included English Wikipedia ZIM is a 100-article test fixture. | **Functional but too small** for broad technical, agricultural, medical, or preparedness research. |

## AI and source-library behavior

The bundled Qwen3 0.6B model generates a real general response offline. The five tested high-risk prompt categories (food outage, tornado shelter, chemical water treatment, wildfire evacuation, and severe bleeding) returned a fixed notice directing the user to original sources, with no citations. The UI itself worked, but this means the AI is not an emergency-response feature. The keyword guard is incomplete and can be bypassed with alternate phrasing; a blocked prompt is not proof that an unblocked answer is safe. The original source files remain the authority where provided.

The Source Library and Kiwix provide access to locally stored content, but content is sparse. The flood pack appeared in the browser source index after transfer and its document was indexed by N.O.M.A.D.; the generated page is visually plain and metadata-heavy. Start Here accurately describes many limits and explains optional pack transfer; reference-pack installation currently requires terminal commands, which is a barrier for a nontechnical field user.

## Verdict and release implications

**Technical offline appliance test: PASS for the reported VM configurations. Preparedness usefulness: FAIL.** A user can boot, open local services, ask general questions, search a small archive, and view a detailed map in one region. The system does not yet provide broad enough trusted material or navigation to cover a variety of disasters. The AI must not be marketed as emergency or medical guidance.

Before recommending physical field use, the project still needs user-selected geographic coverage, licensed and source-reviewed packs for high-priority hazards, a larger useful offline reference collection, a nontechnical offline content-import path, and physical hardware/media validation. Any new content must pass individual source, license, attribution, size, checksum, and in-application usability review. This assessment does not approve redistribution or a public release.
