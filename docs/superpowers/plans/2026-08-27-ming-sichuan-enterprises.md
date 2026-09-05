# Ming and Sichuan Enterprise Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give MNG a complete, representative enterprise roster and replace SIC/SCG's unbalanced five-institution MIO list with seven historically grounded Sichuan institutions.

**Architecture:** Keep civilian designers and military industrial organizations separate, following the current `common/ideas` and `common/military_industrial_organization/organizations` structure. MNG gains new MNG-prefixed records based on selected existing faction institutions; SIC and SCG continue to share one roster, but their MIO categories become infantry, ammunition, artillery, land transport, and river shipping instead of three overlapping infantry entries.

**Tech Stack:** Hearts of Iron IV Clausewitz data files, Simplified Chinese localisation, Python static-contract tests.

**Spec:** User-approved chat design, 2026-08-27: SIC/SCG has seven historical Sichuan institutions; MNG receives five civilian concerns and ten cross-faction representative MIOs.

## Global Constraints

- Do not stage, commit, push, or upload Git changes.
- Use only existing focus/MIO icon assets.
- Keep all existing GOS, ROC, STG, GPS/SRC, XBJ, SIC, and SCG records intact.
- Use MNG-prefixed identifiers for all central-Ming additions.
- SIC/SCG additions must be 1930s Sichuan entities; do not invent an independent tank or aircraft manufacturer.
- Every new user-facing identifier requires Simplified Chinese name and description localisation.

---

### Task 1: Lock the desired rosters in a failing static contract

**Files:**
- Create: `tests/validate_ming_sichuan_enterprises.py`
- Test: `tests/validate_ming_sichuan_enterprises.py`

**Interfaces:**
- Consumes: Clausewitz MIO records in `common/military_industrial_organization/organizations/*.txt` and concern records in `common/ideas/*.txt`.
- Produces: a zero-exit static check for exact IDs, allowed tags, category coverage, state/availability gates, and localisation keys.

- [ ] **Step 1: Write the failing test**

```python
MNG_CIVIL = {
    "MNG_guojia_tielu_zongju",
    "MNG_shuntian_jianshe_zonggongshu",
    "MNG_dongbei_gongye_jituan",
    "MNG_hanjiang_youse_jituan",
    "MNG_yangzi_dianqihua_kaifaju",
}
SICHUAN_MIOS = {
    "TOD_sichuan_chengdu_arsenal_organization",
    "TOD_sichuan_chongqing_ammunition_organization",
    "TOD_sichuan_huaxing_machine_organization",
    "TOD_sichuan_chongqing_weapon_repair_organization",
    "TOD_sichuan_beichuan_railway_organization",
    "TOD_sichuan_minsheng_machine_works_organization",
    "TOD_sichuan_zhonghua_shipyard_organization",
}

assert all("tag = MNG" in mio_blocks[mio] for mio in MNG_MIOS)
assert all("tag = SIC" in mio_blocks[mio] and "tag = SCG" in mio_blocks[mio] for mio in SICHUAN_MIOS)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/validate_ming_sichuan_enterprises.py`

Expected: FAIL because MNG records and the three new Sichuan MIOs do not yet exist.

- [ ] **Step 3: Do not implement until the failure names missing records**

Use the failure output to verify that the test is testing missing production records rather than malformed test parsing.

### Task 2: Add MNG civilian concerns and ten representative MIOs

**Files:**
- Create: `common/ideas/MNG_companies.txt`
- Create: `common/military_industrial_organization/organizations/MNG_organization.txt`
- Create: `localisation/simp_chinese/TOD_MNG_companies_l_simp_chinese.yml`
- Test: `tests/validate_ming_sichuan_enterprises.py`

**Interfaces:**
- Consumes: generic MIO includes already used by GOS, ROC, and STG.
- Produces: five `MNG_*` civilian concerns and ten `MNG_*_organization` records allowed only for `MNG`.

- [ ] **Step 1: Add the five civilian concerns**

Use `industrial_concern` for National Railway, Shuntian Construction, Northeast Industry, and Hanjiang Nonferrous; use `electronics_concern` for Yangtze Electrification. Each record uses `allowed = { original_tag = MNG }` and an existing generic concern picture.

- [ ] **Step 2: Add the ten MIOs with one clear category each**

```text
MNG_qiantang_engineering_organization      generic_infantry_tank_organization
MNG_wuyi_heavy_industry_organization       generic_heavy_tank_organization
MNG_changjiang_arms_organization           generic_infantry_equipment_organization
MNG_luoyang_ordnance_organization          generic_artillery_organization
MNG_tangshan_heavy_machine_organization    generic_motorized_mechanized_organization
MNG_baoding_aircraft_organization           generic_cas_aircraft_organization
MNG_kaifeng_aviation_organization           generic_medium_aircraft_organization
MNG_datong_heavy_aircraft_organization      generic_heavy_aircraft_organization
MNG_jiangnan_naval_repair_organization      generic_task_force_ship_organization
MNG_fuzhou_shipyard_organization            generic_submarine_organization
```

All records use `allowed = { tag = MNG }`, existing generic or source-equivalent icon assets, and no regional-state gate.

- [ ] **Step 3: Add complete Chinese localisation**

Include visible names and concise descriptions explaining the institution's technical role and its selected regional source. Save localisation with UTF-8 BOM.

- [ ] **Step 4: Run the focused test**

Run: `python tests/validate_ming_sichuan_enterprises.py`

Expected: MNG checks advance; SIC/SCG roster checks still fail until Task 3.

### Task 3: Rebuild the shared SIC/SCG MIO roster around verified Sichuan entities

**Files:**
- Modify: `common/military_industrial_organization/organizations/SIC_SCG_organization.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_SCG_companies_l_simp_chinese.yml`
- Modify: `tests/validate_sichuan_enterprises.py`
- Test: `tests/validate_ming_sichuan_enterprises.py`
- Test: `tests/validate_sichuan_enterprises.py`

**Interfaces:**
- Consumes: existing SIC/SCG focus-gated traits and the states 830 (Chongqing) and 831 (Chengdu).
- Produces: seven shared MIOs that preserve current focus-linked traits and replace only the inaccurate institution/category assignments.

- [ ] **Step 1: Preserve four proven military institutions**

Keep Chengdu Arsenal, Chongqing Weapon Repair Office, Chuankang Pacification Ammunition Factory, and Huaxing Machine Works. Rename the Chuankang record to a Chongqing ammunition identifier and assign it to an ammunition/support-compatible MIO include; retain existing weapon-order traits under the compatible record.

- [ ] **Step 2: Replace the unsupported telecom factory and add two historical transport/ship institutions**

```text
TOD_sichuan_beichuan_railway_organization          generic_motorized_mechanized_organization
TOD_sichuan_minsheng_machine_works_organization    generic_raider_ship_organization
TOD_sichuan_zhonghua_shipyard_organization         generic_escort_ship_organization
```

All seven shared records allow SIC and SCG (including their original tags), with Chengdu/Chongqing state gates matching the existing pattern. Use only existing generic MIO icons.

- [ ] **Step 3: Localise institution names, role descriptions, and all new traits**

Descriptions must state the function rather than inventing historical claims: railway logistics, river-vessel repair, and river shipping construction.

- [ ] **Step 4: Update the original enterprise regression test**

Replace the hard-coded five-MIO expectation with the seven approved IDs and assert category diversity: infantry/ammunition, artillery, motorized logistics, raider ship, and escort ship.

- [ ] **Step 5: Run both focused checks**

Run: `python tests/validate_sichuan_enterprises.py; python tests/validate_ming_sichuan_enterprises.py`

Expected: PASS with seven SIC/SCG MIOs and five/ten MNG civilian/MIO entries.

### Task 4: Full regression and delivery audit

**Files:**
- Test: `tests/validate_sichuan_enterprises.py`
- Test: `tests/validate_ming_sichuan_enterprises.py`
- Test: `tests/validate_sic_wubei_route.py`
- Test: `tests/validate_scg_postrevolution_redesign.py`
- Test: `tests/validate_sic_scg_constitutional_routes.py`

**Interfaces:**
- Consumes: all completed data records.
- Produces: evidence that enterprise work did not break existing Sichuan focus, route, or localisation contracts.

- [ ] **Step 1: Run the complete static suite**

Run:

```powershell
python tests/validate_sichuan_enterprises.py
python tests/validate_ming_sichuan_enterprises.py
python tests/validate_sic_wubei_route.py
python tests/validate_scg_postrevolution_redesign.py
python tests/validate_sic_scg_constitutional_routes.py
python -m compileall -q tests
```

Expected: every command exits 0 without diagnostics.

- [ ] **Step 2: Review only the intended files**

Run `git diff --` against the files listed above. Verify no unrelated files were changed. Do not stage, commit, push, or upload anything.
