# Field-use assessment: disaster-preparedness scenarios

Date: 2026-11-05
Assessment: **Not suitable as a standalone disaster-preparedness computer.**

This review checks the fresh customer desktop, bundled applications, offline content, and recorded guest tests. The candidate showed its FieldOS wallpaper and dock; Firefox visibly rendered the Nashville map. Kiwix search returned a local result and the source-library index responded over loopback. Start Here and Command Center shortcuts were visible but were not separately launched in this exact install. This is a content-coverage review, not a clinical, emergency-response, or field trial.

## Tested installation and interface

The latest clean no-NIC unattended test is from source commit
`9c59a5f63cf6a2b35b7489a45cf53c0fc93d2f19`. It installed, completed firstboot,
ran seven services, generated local inference, loaded embeddings, indexed the
core reference documents, searched Kiwix and the source library, visibly
rendered the statewide map in Firefox at eight locations, and passed two
reboots. Report and screenshots:
`/mnt/shared/fieldos-e2e/20261105T031700Z-1734990/report.md`.

The latest customer-mode ISO candidate was built from source commit
`9c59a5f63cf6a2b35b7489a45cf53c0fc93d2f19`:
`/mnt/shared/fieldos-releases/fieldos-customer-offline-9c59a5f.iso`, SHA-256
`4e9800fc6facf698d2408579b42375e9d6fc31fbd38896ff2e68ada6d2654c74`. Interactive
account and disk selection, no-NIC installation, firstboot, the branded desktop,
all six content packs, local AI, embeddings, Kiwix search, a zoom-13 Nashville
browser render, and two reboots were verified. Report and screenshots are in
`/mnt/shared/fieldos-e2e/customer-offline-9c59a5f-20261105/`. Ubuntu's standard
media-removal/restart handoff reached Ubuntu's standard prompt. Ejecting the ISO
and pressing Enter powered off the VM; a normal power-on booted the installed
disk. The installation itself succeeded, but the VM did not restart itself,
so installer handoff acceptance remains partial. Physical USB behavior is
untested.

The current customer image contains the six-pack core payload. Neither test VM
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
| Injury or medical emergency | The ISO includes a narrow NIOSH heat-illness text reference (3 indexed chunks); an optional CDC checklist names skills but gives no procedures. No general first-aid or trauma manual is bundled. | **Very limited source available.** The NIOSH source is worker-focused; do not rely on the AI for medical decisions. |
| Communications outage | An optional FieldOS household communications planner can be transferred from removable media; its pack validator and host-side installer generated a local source index. It helps record contacts, meeting places, and fallbacks. It is not bundled in the ISO, does not send messages or alerts, and has not yet been checked in a running guest. | **Planning aid only.** No radio communication or live connectivity is provided. |
| Travel, navigation, or loss of GPS | The latest unattended image visibly renders zoom-13 maps at eight urban and rural Tennessee locations; the customer install visibly rendered Nashville. World/U.S. maps are overview-only through zoom 5. There is no verified GPS positioning, route calculation, trail data, or offline navigation. | **Useful statewide map viewer, not navigation.** GPS and routing remain unverified. |
| Broad reference lookup | Kiwix opens and returns search results, but the included English Wikipedia ZIM is a 100-article test fixture. The 2026 Southeastern vegetable handbook is now bundled and indexed as 678 chunks. | **Functional but too small** for broad technical, agricultural, medical, or preparedness research. |

## AI and source-library behavior

The bundled Qwen3 0.6B model generates a real general response offline. The five tested high-risk prompt categories (food outage, tornado shelter, chemical water treatment, wildfire evacuation, and severe bleeding) returned a fixed notice directing the user to original sources, with no citations. The UI itself worked, but this means the AI is not an emergency-response feature. The keyword guard is incomplete and can be bypassed with alternate phrasing; a blocked prompt is not proof that an unblocked answer is safe. The original source files remain the authority where provided.

The Source Library and Kiwix provide access to locally stored content, but content is sparse. In the latest interactive customer install, all six core packs activated and their nine source documents indexed as 689 chunks. The generated source index is plain and metadata-heavy. Start Here explains many limits and optional pack transfer; reference-pack installation still needs a nontechnical, fully graphical workflow.

## Verdict and release implications

**Technical offline appliance test: PASS for the reported VM configurations. Preparedness usefulness: FAIL.** A user can boot, open local services, ask general questions, search a small archive, and view a detailed map in one region. The system does not yet provide broad enough trusted material or navigation to cover a variety of disasters. The AI must not be marketed as emergency or medical guidance.

Before recommending physical field use, the project still needs user-selected geographic coverage, licensed and source-reviewed packs for high-priority hazards, a larger useful offline reference collection, a nontechnical offline content-import path, and physical hardware/media validation. Any new content must pass individual source, license, attribution, size, checksum, and in-application usability review. This assessment does not approve redistribution or a public release.
