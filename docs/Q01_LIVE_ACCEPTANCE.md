# Q01 · Application-specific live acceptance receipts

**Backlog acceptance:** *"Seeded broken feature fails acceptance even with green CI; release SHA/URL and browser/test observation persisted."*
**First target application:** Repository Town (a 3D browser game in [joshualparris/JoshMemory](https://github.com/joshualparris/JoshMemory)).

## What a receipt proves

[`scripts/acceptance/repository_town_receipt.mjs`](../scripts/acceptance/repository_town_receipt.mjs) drives a real Chromium at **desktop (1280×800)** and **phone (412×915, touch)** sizes:

| Check | User-facing behaviour, not HTTP 200 |
|---|---|
| `load` | the 3D canvas renders with WebGL, the loading screen clears, and no page errors occur |
| `primary_interaction` | the player walks into the café and **uses the counter with real input** (E key on desktop, ✋ tap on phone); its panel must actually be visible |
| `touch_layout` (phone) | the ✋ button and the joystick sit inside the viewport and clear of the minimap |
| `persistence` | after the game's autosave, a reload puts the player back inside the café |
| `no_page_errors` | no uncaught errors across the whole journey |

Each receipt is JSON bound to the release the site itself reports (`release.json` → `sourceCommit`, `contentHash`). It also records the URL, the browser version, start and finish times, each check's observation and the SHA-256 of every screenshot taken. A failed check fails the run.

## Seeded-fault proof

The workflow [`q01-live-acceptance.yml`](../.github/workflows/q01-live-acceptance.yml) builds JoshMemory main and requires every journey to **PASS**. It then injects one fault a player would notice (the counter's panel never appears), shows that the app's unit tests **still pass**, and requires acceptance to **FAIL**. A third job checks the **live production URL** and keeps its receipt as an artifact.

### Local evidence (authoring session, release `6e67dd3`)

| Build | Unit tests (first-day, staffed-counters, shop-interiors, hotel-lobby, skills) | Acceptance |
|---|---|---|
| clean (`contentHash 5f0a74a5…`) | pass | **PASS 9/9** |
| seeded fault (`contentHash 6cc2a5b4…`) | **pass (5/5)** | **FAIL 7/9** — `desktop.primary_interaction` and `phone.primary_interaction`: "using Coffee counter opened no visible panel" |

The seeded-fault receipt carries the same `sourceCommit` but a different `contentHash`, so the two builds can't be confused.

**The harness's own first bug.** The first clean run *failed* `primary_interaction`, although the screenshot showed the panel open. The harness tested `offsetParent`, which is always null for `position: fixed` elements. It now uses computed style and size. This is the kind of false negative a receipt must be checked for, so every receipt keeps its screenshots.

## Limits

- Headless Chromium with software WebGL is not a physical phone or GPU. Real-device acceptance is still a human step.
- The harness uses the game's test hook to fast-travel and set the clock. The interaction under test uses real key and tap input.
- A PASS covers these journeys on this release only, not the whole game.
- **Not yet integrated with AgentWitness (I01/A04).** The receipt is not signed or broker-witnessed. Until it is, it's strong evidence but not a hardened attestation.

**Status:** the mechanism is demonstrated locally and the CI workflow is added. Q01 depends on **I01**, so it stays **PARTIALLY COMPLETE** until a receipt flows into the witnessed evidence chain and a CI run confirms the three jobs.
