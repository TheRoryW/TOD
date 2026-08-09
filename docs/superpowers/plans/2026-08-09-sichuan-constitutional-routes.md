# SIC and SCG Constitutional Routes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add playable SIC constitutional-monarchist and SCG socialist-bicameral routes, including political decisions, recovery loops, and separate national-unification endings.

**Architecture:** Existing focus trees remain the entry point. New focus branches unlock country-scoped variables, dynamic modifiers, decision categories, and country events. A static Python validator asserts every new focus, decision, event, modifier, localisation key, and scripted trigger exists before the content is treated as complete.

**Tech Stack:** Hearts of Iron IV Clausewitz scripts, scripted triggers/effects, dynamic modifiers, decisions, country events, YAML localisation, Python standard library.

## Global Constraints

- Preserve all existing uncommitted user changes and touch only SIC/SCG-related files plus the validator and design documents.
- Keep `SIC.gongye` and `SIC.minzhong` semantics unchanged: higher values remain worse.
- Use generic focus icons for newly introduced content; do not require new image assets in this implementation.
- Do not replace the existing SIC/SCG focus trees or current uprising/recovery systems.
- All new localisation is Simplified Chinese and all IDs use the `SIC_`, `SCG_`, or `TODSIC.` prefixes.

---

### Task 1: Establish static validation for the constitutional routes

**Files:**
- Create: `tests/validate_sic_scg_constitutional_routes.py`
- Verify: SIC/SCG focus, decision, event, idea, modifier, scripted trigger, and localisation files

- [ ] **Step 1: Write the failing test**

Create a standard-library Python validator that requires `SIC_qingzhengxi_sichuan`, `SIC_sichuan_jibenfa`, `SIC_daming_lixian_guo`, `SCG_jianli_renmin_dahui`, `SCG_jianli_zhengdanghui`, `SCG_sichuan_shehuizhuyi_xianfa`, and `SCG_zhonghua_shehuizhuyi_gongheguo`, plus their decision categories, dynamic modifiers, events, scripted triggers, and localisation keys.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: failure naming missing constitutional-route IDs.

- [ ] **Step 3: Keep the validator focused**

Require balanced braces for Clausewitz files and reject absent localisation keys; do not try to parse all Clausewitz grammar.

### Task 2: Implement SIC’s clear-government constitutional route

**Files:**
- Modify: `common/national_focus/chuanyudifangsi.txt`
- Create: `common/decisions/categories/SIC_constitutional_reform.txt`
- Create: `common/decisions/SIC_constitutional_reform.txt`
- Modify: `common/dynamic_modifiers/TOD_SIC_modifiers.txt`
- Modify: `common/ideas/SIC_idea.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`

- [ ] **Step 1: Implement the focus branch**

Add the SIC clear-government sequence from `SIC_qingzhengxi_sichuan` through `SIC_sichuan_moshi`, then the constitutional national-unification sequence through `SIC_daming_lixian_guo`. Gate constitutional milestones on `SIC.qingzhengxi` and `SIC.xianzheng`.

- [ ] **Step 2: Implement the decisions and modifiers**

Add “四川新政” decisions that trade political power, factories, and short-term military support for lower crisis values and higher clear-government/constitutional values. Add “宪政统一” decisions that support constitutional politics or prepare legal wars against the existing Chinese rival tags.

- [ ] **Step 3: Add SIC national spirits and localisation**

Add the constitutional-experiment dynamic modifier, the completed-constitution national spirit, all focus/decision/tooltips, and change SIC’s liberal-democracy party display to the clear-government constitutional faction.

- [ ] **Step 4: Run validation**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: SIC requirements pass; SCG requirements remain the only missing set.

### Task 3: Implement SCG’s socialist multi-party bicameral route

**Files:**
- Modify: `common/national_focus/sichuangemingzhengfu.txt`
- Create: `common/decisions/categories/SCG_bicameral_politics.txt`
- Create: `common/decisions/SCG_bicameral_politics.txt`
- Modify: `common/dynamic_modifiers/TOD_SCG_modifiers.txt`
- Modify: `common/ideas/SCG_idea.txt`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`

- [ ] **Step 1: Implement the political focus branch**

From `SCG_gemingchenggong`, add the first revolutionary meeting, socialist multi-party recognition, People’s Assembly, Party Council, joint procedure, responsible people’s committee, socialist constitution, and national-unification focuses.

- [ ] **Step 2: Implement two-chamber and recovery decisions**

Add decisions that alter `SCG.renmin_shouquan`, `SCG.dangji_xietiao`, and `SCG.chongjian`; include meetings, cross-party coordination, minority amendments, factory recovery, railway repair, grain security, demobilisation, and education/health recovery.

- [ ] **Step 3: Implement coalition and threshold spirits**

Add national spirits for cooperative, contested, and crisis two-chamber states; use a scripted effect to update them after each political decision. Keep existing economic and army paths as policy programmes rather than deleting them.

- [ ] **Step 4: Run validation**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: all content IDs and braces pass.

### Task 4: Add shared unification gates, events, and end-to-end checks

**Files:**
- Create: `common/scripted_triggers/SIC_SCG_unification.txt`
- Create: `common/scripted_effects/SCG_bicameral_effects.txt`
- Modify: `events/SiChuan.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`

- [ ] **Step 1: Implement end-state triggers**

Require the existing main Chinese rival tags to be eliminated before final national constitutional conferences. Keep SIC and SCG final identities separate.

- [ ] **Step 2: Implement country events**

Add SIC’s constitutional proclamation and SCG’s two-chamber founding, cabinet crisis, and national socialist constitution events. Every event must be triggered only by new focus/decision IDs and must be one-shot where appropriate.

- [ ] **Step 3: Run static checks and review scope**

Run: `python tests/validate_sic_scg_constitutional_routes.py`; then run `git diff --check` and inspect only SIC/SCG-related diffs.

- [ ] **Step 4: Commit**

Stage only the files listed in this plan and commit with: `git commit -m "feat: add Sichuan constitutional routes"`.
