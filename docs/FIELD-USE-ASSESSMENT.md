# Field-use assessment: disaster-preparedness scenarios

Date: 2026-11-05
Assessment: **Not suitable as a standalone disaster-preparedness computer.**

This review checks an actual fresh customer-mode installation, its installed
desktop and applications, and offline content behavior. Candidate
`/mnt/shared/fieldos-releases/fieldos-customer-8c81d64.iso` (SHA-256
`3dd16528cde1cbbfa7dac9f8a4cea325a09857eb58a5c9b079d5917ab5c6147d`) completed
interactive identity/disk selection, installation, installed-disk boot,
firstboot, and two reboots in a disposable no-NIC UEFI VM. The test account
completed GNOME first-run setup; the desktop showed FieldOS wallpaper, dark
theme, accent color, and dock. Command Center, AI Assistant, Kiwix, Source
Library, and Maps were opened in Firefox. A separate manual add-on test imported
an optional communications worksheet from read-only media through the desktop
UI; the Source Library displayed it and its local document persisted through
one further reboot. This is a VM and optical-media test, not a physical field
trial or physical USB test.

The exact run evidence and screenshots are in
`/mnt/shared/fieldos-e2e/customer-8c81d64-20261105/diagnostics.md` and its
`viewer/` directory. The customer candidate is still private engineering test
material and is not approved for redistribution.

## Tested installation and interface

The installed guest had no virtual NIC or default route. Firstboot completed;
all seven N.O.M.A.D. containers returned after two reboot cycles. Firefox
visibly rendered statewide zoom-13 maps at Memphis, Nashville, Knoxville,
Chattanooga, Clarksville, Jackson, Johnson City, and rural Big South Fork. The
bundled CPU Qwen3 1.7B model generated real responses; the embedding model
returned 768-dimensional vectors. A real RAG answer cited the Southeastern
vegetable handbook, and a tornado shelter prompt returned the configured
source-directed refusal. Kiwix searched the bundled 100-article Wikipedia
fixture. N.O.M.A.D. indexed 10 core files / 690 chunks. A manual optional pack
import then appeared in the Source Library and its document endpoint returned
HTTP 200; its pack and reference index persisted across an additional reboot.

## Scenario walk-through

| Situation | What an offline user can actually use | Assessment |
|---|---|---|
| Power outage and food spoilage | One CDC source document, “Eat Safe Food After a Power Outage,” is bundled and linked from Start Here/Source Library. The tested AI safety guard refuses food-safety prompts. | **Narrow help available.** No broader food storage, cooking-fuel, or household power reference was verified. |
| Water service interruption | One CDC emergency-water PDF is bundled. It is available as a primary source; the AI guard refuses water-treatment questions. | **Narrow source available.** It does not cover every contaminant or local water advisory. Read the document directly; do not treat boiling as a universal treatment. |
| Tornado | A text-only NWS “What to Do During a Tornado” reference is bundled and indexed. The AI guard refuses tested tornado-shelter prompts. | **Basic source available.** No live alerts, local shelter database, or current warning feed works offline. |
| Hurricane or winter storm | Three NWS-derived FieldOS summaries in `us-weather-safety` 1.0.1 were installed and indexed from the core payload in both unattended and current interactive no-NIC tests. | **Source available.** No forecasts or alerts are provided. |
| Wildfire or evacuation | No dedicated wildfire source is bundled. The AI guard refused one tested wildfire prompt, but prior tests found alternate wording can bypass the keyword guard. | **Not dependable.** A refusal is not safety certification or evacuation guidance. |
| Flood | The FieldOS-edited NWS summary in `us-flood-safety` 1.0.0 was installed and indexed from the core payload in both unattended and current interactive no-NIC tests. | **Source available.** No current flood alerts, flood-zone data, or safe routing are provided. |
| Injury or medical emergency | The ISO includes a narrow, worker-focused NIOSH heat-illness reference and a brief MedlinePlus First Aid overview. An optional CDC checklist names skills but gives no procedures. No general first-aid or trauma manual is bundled. | **Very limited source available.** These items are not procedure manuals; do not rely on AI for medical decisions. |
| Communications outage | The optional FieldOS household planner was imported through GNOME from read-only optical media on the current customer guest. It appeared in the Source Library, its local document served successfully, and its pack/index survived a further reboot. It is not bundled in the customer ISO and does not send messages or alerts. A prior clone test found chat did not reliably extract its contact fields. | **Planning aid only.** Open and read the original worksheet; do not rely on AI retrieval for its fields. No radio communication or live connectivity is provided. |
| Travel, navigation, or loss of GPS | The current customer install visibly rendered zoom-13 statewide maps at eight urban and rural Tennessee locations. World/U.S. maps are overview-only through zoom 5. There is no verified GPS positioning, route calculation, trail data, or offline navigation. | **Useful statewide map viewer, not navigation.** GPS and routing remain unverified. |
| Broad reference lookup | Kiwix opens and returns search results, but the included English Wikipedia ZIM is a 100-article test fixture. The 2026 Southeastern vegetable handbook is now bundled and indexed as 678 chunks. | **Functional but too small** for broad technical, agricultural, medical, or preparedness research. |

## AI and source-library behavior

The current candidate selected Qwen3 1.7B on CPU and generated real responses offline. A tornado shelter prompt returned the configured notice directing users to original sources. In an earlier five-category test (food outage, tornado shelter, chemical water treatment, wildfire evacuation, and severe bleeding) the 0.6B model returned the same fixed notice, but alternate wording can bypass the keyword guard. A blocked prompt is not proof that an unblocked answer is safe. The original source files remain the authority where provided.

The Source Library and Kiwix provide access to locally stored content, but content is sparse. The current interactive install activated eight core packs; firstboot indexed 10 files as 690 chunks, and the Source Library displayed the original documents and their source metadata. Kiwix contains only a 100-article fixture. The graphical optional-pack importer was manually exercised on the current guest and worked with optical media; physical USB insertion/navigation has not been tested. The generated Source Library remains plain and metadata-heavy.

## Verdict and release implications

**Technical offline appliance test: PASS for the reported VM configurations. Preparedness usefulness: FAIL.** A user can boot, open local services, ask general questions, search a small archive, and view a detailed map in one region. The system does not yet provide broad enough trusted material or navigation to cover a variety of disasters. The AI must not be marketed as emergency or medical guidance.

Before recommending physical field use, the project still needs user-selected geographic coverage, licensed and source-reviewed packs for high-priority hazards, a larger useful offline reference collection, a nontechnical offline content-import path, and physical hardware/media validation. Any new content must pass individual source, license, attribution, size, checksum, and in-application usability review. This assessment does not approve redistribution or a public release.
