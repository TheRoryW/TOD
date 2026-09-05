# Hungary Content Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Make the Hungary focus tree reliably playable: remove inactive focus effects, repair misleading or missing tooltips/localisation, add five small immersive decision events, and replace the active copied Czechoslovak officer roster with a coherent Hungarian alternate-history command structure.

**Architecture:** Keep all changes inside the existing Hungary focus, event, character, history, interface, localisation, and static-validator files. The focus tree remains the entry point; each new `HUN.101`–`HUN.105` event is `is_triggered_only` and is called only from its associated focus. Real effects use locally validated HOI4 effect syntax. The country history recruits only Hungarian characters; native advisers are also given command roles based on the vanilla Hungary character patterns and adapted to the independent Danubian setting.

**Tech Stack:** Paradox Clausewitz script; HOI4 localisation YAML; Python `unittest` static validator; local vanilla Hungary files at `D:\Game\Hearts of Iron IV\common\characters\HUN.txt` as the reference baseline.

**Spec:** `docs/superpowers/specs/2026-08-23-hungary-content-and-portrait-overhaul-design.md`

## Global constraints

- Preserve all unrelated existing worktree changes. Do not reset, reformat, or stage broad paths.
- Do not add Czech/Slovak commanders or `CZE` portrait references to active Hungary content.
- Do not alter state ownership, borders, or other countries as part of these fixes.
- Every player-facing new effect needs matching English and Simplified Chinese localisation.
- Prefer existing, validated effects: `add_manpower`, experience gains, `add_political_power`, stability/war-support changes, and `add_tech_bonus` categories already used locally.
- Do not launch the game until static validation is clean; no claim of in-game validation without a recorded game run.

---

## Task 1: Turn the Hungary audit into red tests

**Files:**

- Modify: `tests/validate_hungary_content.py`
- Read: `common/national_focus/hungary.txt`
- Read: `events/Hungary.txt`
- Read: `common/characters/HUN.txt`
- Read: `history/countries/HUN.txt`
- Read: `localisation/english/TOD_Hungary_l_english.yml`
- Read: `localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml`

- [ ] **Step 1: Add failing tests that express the audited contract.**

  Add focused helpers that strip comments, extract focus blocks by identifier, and extract top-level character blocks. Add tests that:

  - require localisations for `HUN_geminzupingdeng_xiaoguo` and `HUN_lianhefeiji_xiaoguo` in both languages;
  - reject `add_to_variable` for the six audited dead variables: `HUN_shaominfankang`, `HUN_lujungongji`, `HUN_lujunfangyu`, `HUN_shandi`, `HUN_shiying`, `HUN_renyuan`, `HUN_haijunrenyuan`, and `HUN_peixun`;
  - require `HUN.101`–`HUN.105` to be defined as triggered-only events, invoked by exactly one Hungary focus each, and fully localised;
  - reject `HUN_CZE_` / Czech copied character IDs and `GFX_*CZE*` references in active Hungary country history and character definitions;
  - require the alternate command roster to contain the native command roles listed in Task 4.

- [ ] **Step 2: Run the test suite to confirm RED.**

  Run `python tests/validate_hungary_content.py`. Record each expected failure; the run must fail only because the new requirements have not yet been implemented.

- [ ] **Step 3: Commit the test-only change selectively.**

  Stage only `tests/validate_hungary_content.py`; do not stage existing user changes. Commit message: `test: define Hungary content overhaul contract`.

## Task 2: Replace no-op military focus effects with real, legible effects

**Files:**

- Modify: `common/national_focus/hungary.txt`
- Modify: `localisation/english/TOD_Hungary_l_english.yml`
- Modify: `localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml`
- Test: `tests/validate_hungary_content.py`

- [ ] **Step 1: Confirm the specific failing no-op tests.**

  Run the focused validator after Task 1. Verify that only the six audited dead-variable focus blocks are reported, so election variables remain untouched.

- [ ] **Step 2: Implement real gameplay effects in the six focus blocks.**

  In `HUN_geminzupingdeng`, remove the unused ethnic-resistance variable and retain the existing stability/war-support result; add its missing custom-effect text.

  Replace each other dead-variable pair with these direct effects, then adjust its custom tooltip to describe those exact results:

  | Focus | Real effects |
  | --- | --- |
  | `HUN_tezhonghuazuozhan` | `army_experience = 25`; one 50% `special_forces_doctrine` research bonus |
  | `HUN_shandixunlian` | `army_experience = 20`; one 50% `special_forces_doctrine` research bonus |
  | `HUN_qihoushiyin` | `army_experience = 15`; one 50% `infantry_weapons` research bonus |
  | `HUN_zhaomuhaijunrenyuan` | `add_manpower = 10000`; `navy_experience = 25` |
  | `HUN_jiaqiangrenyuanpeixun` | `navy_experience = 25`; one 50% `naval_doctrine` research bonus |

  Use one effect block per stated reward; do not duplicate bonuses through event choices.

- [ ] **Step 3: Localise the exact player-facing result in both languages.**

  Add the two missing custom effect keys. Update `HUN.9.tt` through `HUN.13.tt` where needed so their stated percentages/resources match the direct game effects instead of the former variable placeholders. Keep YAML formatting and BOM/newline convention consistent with each file.

- [ ] **Step 4: Run the static test suite to confirm GREEN.**

  Run `python tests/validate_hungary_content.py`; confirm the no-op-variable and tooltip-localisation tests pass.

- [ ] **Step 5: Commit this isolated effect repair selectively.**

  Stage only the three Task 2 files. Commit message: `fix: give Hungary military focuses real effects`.

## Task 3: Add five small focus-linked narrative events

**Files:**

- Modify: `events/Hungary.txt`
- Modify: `common/national_focus/hungary.txt`
- Modify: `localisation/english/TOD_Hungary_l_english.yml`
- Modify: `localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml`
- Test: `tests/validate_hungary_content.py`

- [ ] **Step 1: Add failing event-presence and localisation checks.**

  Confirm all ten missing event title/description/option keys per language are detected before implementation. Ensure the tests check the event IDs rather than matching natural-language text.

- [ ] **Step 2: Implement the event records.**

  Define exactly the following triggered-only events in `events/Hungary.txt`, using the existing `HUN` namespace and safe direct effects. Each event should have one short narrative description and two choices whose effects differ meaningfully without changing borders or creating foreign dependencies:

  | ID | Calling focus | Theme | Choice reward profiles |
  | --- | --- | --- | --- |
  | `HUN.101` | `HUN_fazhanduonaohejinjidai` | Danube recovery programme | civilian recovery: stability + political power; logistics priority: infrastructure construction speed research bonus + political power |
  | `HUN.102` | `HUN_geminzupingdeng` | civic compact for an independent Danubian state | civic guarantees: stability; common service: manpower + war support |
  | `HUN.103` | `HUN_tezhonghuazuozhan` | professional frontier detachments | mountain school: army experience; mobile staff: political power + army experience |
  | `HUN.104` | `HUN_zhaomuhaijunrenyuan` | Danube flotilla volunteers | trained reservists: navy experience; broad levy: manpower |
  | `HUN.105` | `HUN_duiwaizhengce` | foreign-policy review | diplomatic mission: stability + political power; security review: war support + army experience |

  Use `add_tech_bonus` only for the verified `infantry_weapons`, `naval_equipment`, `air_equipment`, `naval_doctrine`, or `special_forces_doctrine` categories. If an intended reward would require an unverified modifier, replace it with experience or political power rather than inventing script syntax.

- [ ] **Step 3: Add exactly one event call to each associated focus.**

  Place `country_event = { id = HUN.101 }` through `.105` in the corresponding completion reward blocks. Confirm no focus now calls an existing event twice and none of the new events self-trigger or are mean-time-to-happen events.

- [ ] **Step 4: Localise all events in English and Simplified Chinese.**

  Add title, description, and two option keys for each event (20 keys per language). English must be actual English rather than copied Chinese. Write the Chinese as natural in-game text, not literal English transliteration.

- [ ] **Step 5: Verify event references and grammar.**

  Run `python tests/validate_hungary_content.py`, then a stripped-comment brace-balance check over the focus and event files. Confirm all event requirements pass.

- [ ] **Step 6: Commit the immersive-event slice selectively.**

  Stage only the four Task 3 files. Commit message: `feat: add Hungary focus narrative events`.

## Task 4: Rebuild the active Hungary command roster around Hungarian officers

**Files:**

- Modify: `history/countries/HUN.txt`
- Modify: `common/characters/HUN.txt`
- Modify: `localisation/english/TOD_Hungary_l_english.yml` (only if new display keys are necessary)
- Modify: `localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml` (only if new display keys are necessary)
- Test: `tests/validate_hungary_content.py`
- Reference: `D:\Game\Hearts of Iron IV\common\characters\HUN.txt`

- [ ] **Step 1: Confirm RED for copied roster removal.**

  Run the Task 1 roster test. Also list every `recruit_character` under the Hungary history file and every `HUN_*` character definition to establish the exact before state.

- [ ] **Step 2: Remove the active copied Czechoslovak roster.**

  Delete the CZE/Slovak recruit lines from `history/countries/HUN.txt`, then remove their now-unreferenced complete character blocks from `common/characters/HUN.txt`. Do not delete native Hungarian leaders or neutral shared assets. The removed roster includes the copied Luža, Šnejdárek, Tesařík, Vojcechovský, Viest, Vicherek, Hasal, Fajfr, Golian, Janoušek, František, Krejčí, Petřík, Kuttelwascher, Svoboda, Havel, Osuský, Čatloš, Tiso, Tuka, Henlein, and Husák entries.

- [ ] **Step 3: Give the retained native roster a coherent alternate-Hungary command identity.**

  Preserve the existing native generals (Géza Lakatos, Iván Hindy, Károly Beregfy, Lajos Veress, Ferenc Feketehalmy-Czeydner, and Aurél Stromfeld). Following the local vanilla character-file role pattern, add active military command roles alongside existing adviser roles for these Hungarian officers:

  | Character | Command role | Alternate-history identity |
  | --- | --- | --- |
  | `HUN_ferenc_szombathelyi` | corps commander, `hill_fighter`, skill 3 | Carpathian frontier professional |
  | `HUN_hugo_sonyi` | corps commander, `engineer`, skill 2 | Danube defensive engineer |
  | `HUN_dezso_laszlo` | corps commander, `organizer`, skill 1 | staff-and-mobilisation officer |
  | `HUN_henrik_werth` | field marshal, skill 3 | conservative cavalry-and-staff marshal |

  Do not inherit `trait_HUN_fascist_sympathies`, German-alignment availability gates, or vanilla DLC-gated structure: this mod’s independent Danubian Hungary should keep these roles available from game start. Use existing mod-compatible traits only (`hill_fighter`, `engineer`, `organizer`) and retain their current adviser functions.

- [ ] **Step 4: Run GREEN roster tests and reference scans.**

  Run the full validator. Search active Hungary history and character files for `CZE`, `czech`, Czech portrait GFX names, and removed character IDs; there must be no active results. Run a stripped-comment brace-balance check for both edited files.

- [ ] **Step 5: Commit the character-only slice selectively.**

  Stage only the edited Task 4 files. Commit message: `feat: rebuild Hungary alternate command roster`.

## Task 5: Full Hungary verification and handoff

**Files:**

- Verify: all files modified by Tasks 1–4

- [ ] **Step 1: Run all static checks.**

  Run `python tests/validate_hungary_content.py`. Run stripped-comment brace-balance checks for `common/national_focus/hungary.txt`, `events/Hungary.txt`, `common/characters/HUN.txt`, and `history/countries/HUN.txt`. Check event/focus IDs, localisation keys, character references, and sprite aliases.

- [ ] **Step 2: Inspect the exact diff without disturbing existing work.**

  Use targeted `git diff --` paths and `git status --short`; report only files intentionally touched by this plan. Do not use `git reset`, `git checkout`, or broad formatting operations.

- [ ] **Step 3: Review and document residual limits.**

  Confirm whether a game launch was available. If not, clearly hand off the static-pass result and request an in-game check of event firing, focus rewards, and portrait rendering.

- [ ] **Step 4: Make the final selective commit only if the user authorises a commit.**

  If commits were not desired, leave changes uncommitted and state so. If authorised, stage only the explicit Hungary files and tests and commit with the final integrated message: `feat: overhaul Hungary content and roster`.
