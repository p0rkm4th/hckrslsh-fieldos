# Field-use assessment: disaster-preparedness scenarios

Date: 2026-11-04  
Assessment: **Not suitable as a standalone disaster-preparedness computer.**

This review follows the installed desktop and its Start Here/Command Center paths as a new offline user, then checks each scenario against bundled source material and the recorded guest tests. It distinguishes actual functional tests from a content-coverage review. It is not a clinical, emergency-response, or field trial.

## Tested installation and interface

The current clean-source unattended test ISO at source `d8653336ea4597df8eb386a83d364c9dca19d290` passed a fresh no-NIC installation, firstboot, local inference, embeddings, Kiwix, visible Middle Tennessee map rendering, optional weather-pack import, and two reboots. Its report is `/mnt/shared/fieldos-e2e/20261104T125608Z-3534340/report.md`; test ISO SHA-256 is `0bd97610307320f5dd725b94eead0745ba61fbff69083d5d43d7f4ff473e2781`.

A separate customer-mode ISO from source `3054c59fe38295d54a316b4da22088582a23d3bc` was installed interactively in a disposable VM. The FieldOS desktop and Command Center opened; the local AI produced a general response, Kiwix search returned results, and Firefox visibly rendered Nashville streets at zoom 13. Local services and these functions persisted through two reboots. Report and user-facing screenshots are in `/mnt/shared/fieldos-e2e/customer-regional-3054c59-20261104/`. That candidate's SHA-256 is `522abcbc4ba04593ce7d1813af43c5c86110b22a41239c13c3e9800f017d1686`.

These are two distinct artifacts. The optional weather-pack transfer was exercised on the newer test ISO, not the customer ISO. Neither VM had a network adapter. These results do not test physical USB media handoff, external weather alerts, physical GPS, or broad geographic coverage.

## Scenario walk-through

| Situation | What an offline user can actually use | Assessment |
|---|---|---|
| Power outage and food spoilage | One CDC source document, “Eat Safe Food After a Power Outage,” is bundled and linked from Start Here/Source Library. The tested AI safety guard refuses food-safety prompts. | **Narrow help available.** No broader food storage, cooking-fuel, or household power reference was verified. |
| Water service interruption | One CDC emergency-water PDF is bundled. It is available as a primary source; the AI guard refuses water-treatment questions. | **Narrow source available.** It does not cover every contaminant or local water advisory. Read the document directly; do not treat boiling as a universal treatment. |
| Tornado | A text-only NWS “What to Do During a Tornado” reference is bundled and indexed. The AI guard refuses tested tornado-shelter prompts. | **Basic source available.** No live alerts, local shelter database, or current warning feed works offline. |
| Hurricane or winter storm | Three NWS-derived FieldOS summaries exist in optional pack `us-weather-safety` 1.0.1. Pack installation and indexing passed on removable media in the no-NIC test. It is not included in the customer ISO. | **Optional only.** The installed baseline cannot be assumed to contain these documents; no forecasts or alerts are provided. |
| Wildfire or evacuation | No dedicated wildfire source is bundled. The AI guard refused one tested wildfire prompt, but prior tests found alternate wording can bypass the keyword guard. | **Not dependable.** A refusal is not safety certification or evacuation guidance. |
| Flood | No dedicated flood guidance or tested flood-specific source was found in the baseline references. | **Not covered.** |
| Injury or medical emergency | No first-aid or trauma manual is bundled. The AI guard refused one severe-bleeding prompt. | **Not covered.** Do not rely on the AI for medical decisions. |
| Communications outage | No radio operation, emergency communications, or contact-plan reference was found in the bundled source set. | **Not covered.** |
| Travel, navigation, or loss of GPS | Firefox renders an interactive Middle Tennessee road map through zoom 13. Global and U.S. maps are overview-only through zoom 5. There is no verified GPS positioning, route calculation, trail data, or offline navigation. | **Useful local map viewer only.** It is useful only in the covered area and is not a navigation system. |
| Broad reference lookup | Kiwix opens and returns search results, but the included English Wikipedia ZIM is a 100-article test fixture. | **Functional but too small** for broad technical, agricultural, medical, or preparedness research. |

## AI and source-library behavior

The bundled Qwen3 0.6B model generates a real general response offline. The five tested high-risk prompt categories (food outage, tornado shelter, chemical water treatment, wildfire evacuation, and severe bleeding) returned a fixed notice directing the user to original sources, with no citations. The UI itself worked, but this means the AI is not an emergency-response feature. The keyword guard is incomplete and can be bypassed with alternate phrasing; a blocked prompt is not proof that an unblocked answer is safe. The original source files remain the authority where provided.

The Source Library and Kiwix provide access to locally stored content, but content is sparse. Start Here accurately describes many limits and explains optional USB packs; reference-pack installation currently requires terminal commands, which is a barrier for a nontechnical field user.

## Verdict and release implications

**Technical offline appliance test: PASS for the reported VM configurations. Preparedness usefulness: FAIL.** A user can boot, open local services, ask general questions, search a small archive, and view a detailed map in one region. The system does not yet provide broad enough trusted material or navigation to cover a variety of disasters. The AI must not be marketed as emergency or medical guidance.

Before recommending physical field use, the project still needs user-selected geographic coverage, licensed and source-reviewed packs for high-priority hazards, a larger useful offline reference collection, a nontechnical offline content-import path, and physical hardware/media validation. Any new content must pass individual source, license, attribution, size, checksum, and in-application usability review. This assessment does not approve redistribution or a public release.
