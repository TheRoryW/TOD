# Russia, Caucasus, and East Wall Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Caucasus, Great Northern War, East Wall victory settlement, and Franco-Iberian exile flows execute in the intended order.

**Architecture:** Country events own country-specific declarations and outcomes. Global progression uses scoped flags only as gates. The East Wall settlement is a Hungarian event with explicit state transfers and releases, avoiding an AI peace-conference outcome.

**Tech Stack:** Hearts of Iron IV Clausewitz scripts, history state files, scripted country events, YAML localisation.

## Global Constraints

- Do not use `replace_path` changes, copy vanilla files, or alter GUI/GFX.
- Preserve the existing tags; CAU is not replaced by a new unified tag.
- Use normal gameplay event timing and country-scoped recipients.
- State 95 belongs to POL from game start; East Wall settlement threshold is 195, 217, 249.

---

### Task 1: Caucasus and northern-war sequence

**Files:**
- Modify: `events/Russia.txt`, `events/FIN.txt`, `common/characters/CAU.txt`
- Modify: `localisation/simp_chinese/TOD_CAU_l_simp_chinese.yml`, `localisation/english/TOD_CAU_l_english.yml`

- [ ] Write a static check that fails while Russia owns the CAU declaration, while no CAU victory flag exists, or while Russia's winter-war trigger lacks the northern-war completion flag.
- [ ] Move the CAU declaration to a CAU-scoped event, add a revolution-front victory event that promotes Budyonny without changing the CAU tag, and add one shared FIN/SWE completion flag.
- [ ] Add Budyonny character and both localisation entries; use a valid CAU portrait reference.
- [ ] Re-run the static check and confirm Russia cannot advance before CAU and northern-war conclusions.

### Task 2: East Wall settlement and Serbia protection

**Files:**
- Modify: `events/Hungary.txt`, `events/Russia.txt`
- Modify: `history/states/95-Nowogrodek.txt`
- Modify: `localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml`, `localisation/english/TOD_Hungary_l_english.yml`

- [ ] Write a static check requiring HUN's settlement trigger to test active RUS war and East Wall control of 195, 217, 249, plus all requested state-transfer IDs.
- [ ] Add the HUN-owned one-shot settlement: transfer Finland, BLT under BLR, BLR, UKR, and POL states; release CAU/ARM/GEO/AZR/KYR; retain RUS in SIB and release FET as RUS subject; end only the Russian war; schedule the Serbian event after 30 days.
- [ ] Add the SER-owned acceptance event that makes SER a HUN subject.
- [ ] Change state 95 start owner to POL without removing its POL core.
- [ ] Re-run the check and validate every referenced tag/state exists.

### Task 3: France, Spain, and Hungarian AI

**Files:**
- Modify: `events/FRA.txt`, `events/SPR.txt`, `common/national_focus/hungary.txt`

- [ ] Write a static check that fails on the duplicate Cachin leader-role addition, Spain's broad `every_country` white peace, or East Wall AI weight below 100.
- [ ] Remove the duplicate French leader role; restrict Spain's white peaces to GER and ENG while preserving its puppet/exile outcome; raise `HUN_dongqiang` AI base/weight to at least 100.
- [ ] Re-run the static check and review the edited event scopes.

### Task 4: End-to-end validation

**Files:**
- Verify: all modified files

- [ ] Run brace-balance and reference checks for event IDs, character IDs, localisation keys, tags, and state IDs.
- [ ] Start the game normally only if no existing user game session is running; inspect a fresh error log for modified-path errors.
- [ ] Do not commit or alter unrelated files.
