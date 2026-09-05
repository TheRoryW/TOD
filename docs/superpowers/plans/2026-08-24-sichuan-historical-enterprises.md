# Sichuan Historical Enterprises Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one shared pool of five historically grounded Sichuan military industrial organizations and four major industrial concerns for SIC and SCG.

**Architecture:** Military organizations live in one shared MIO file and inherit vanilla generic organization trees; industrial concerns live in one shared ideas file. Both countries use the same organization and concern IDs, while territorial control and existing SIC/SCG focuses govern availability. A dedicated static validator protects the exact company count, historical names, state gates, supported equipment classes, localization, and Clausewitz syntax.

**Tech Stack:** Hearts of Iron IV Clausewitz script, military industrial organizations, idea/advisor definitions, Simplified Chinese YAML localization, Python static validation.

**Spec:** `docs/superpowers/specs/2026-08-24-sichuan-enterprises-wubei-scg-redesign-design.md`

## Global Constraints

- Industrial concerns are exactly: 民生实业股份有限公司、华西兴业股份有限公司、重庆电力股份有限公司、天府煤矿公司.
- Military organizations are exactly the five organizations listed in the spec; do not add tank, motorized, aircraft, or naval organizations.
- SIC and SCG share IDs and historical names; do not create duplicate political-regime variants.
- SIC access requires territorial control plus an existing SIC economy or military-industry focus; SCG access requires territorial control plus an existing post-revolution focus.
- Use existing generic MIO and idea artwork only; do not create image files.
- Preserve `common/decisions/SIC.txt` and `common/decisions/SCG.txt` byte-for-byte.
- Work in the current workspace because the target Sichuan content contains uncommitted user work; preserve unrelated changes.
- Do not stage, commit, push, or upload Git changes.

---

### Task 1: Add the enterprise contract validator

**Files:**
- Create: `tests/validate_sichuan_enterprises.py`

**Interfaces:**
- Consumes: `ROOT`, `named_block`, and `localisation_keys` from `tests/validate_sic_scg_constitutional_routes.py`.
- Produces: a standalone command that exits nonzero when a company, state gate, shared-country rule, localization key, or MIO equipment boundary is wrong.

- [ ] **Step 1: Write the failing validator**

Create `tests/validate_sichuan_enterprises.py` with these fixed contracts:

```python
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_sic_scg_constitutional_routes import (  # noqa: E402
    ROOT,
    localisation_keys,
    named_block,
)

MIO_FILE = ROOT / "common/military_industrial_organization/organizations/SIC_SCG_organization.txt"
CONCERN_FILE = ROOT / "common/ideas/SIC_SCG_companies.txt"
LOCALISATION = ROOT / "localisation/simp_chinese/TOD_SIC_SCG_companies_l_simp_chinese.yml"

MIO_CONTRACT = {
    "TOD_sichuan_chengdu_arsenal_organization": ("831", "generic_infantry_equipment_organization"),
    "TOD_sichuan_chongqing_weapon_repair_organization": ("830", "generic_artillery_organization"),
    "TOD_sichuan_chuankang_ammunition_organization": ("831", "generic_infantry_equipment_organization"),
    "TOD_sichuan_huaxing_machine_organization": ("831", "generic_infantry_equipment_organization"),
    "TOD_sichuan_telecom_repair_organization": ("830", "generic_support_equipment_organization"),
}

CONCERN_CONTRACT = {
    "TOD_sichuan_minsheng_industry": "830",
    "TOD_sichuan_huaxi_industry": "831",
    "TOD_sichuan_chongqing_electric": "830",
    "TOD_sichuan_tianfu_coal": "830",
}

FORBIDDEN_COMPANIES = (
    "TOD_sichuan_minsheng_machine",
    "TOD_sichuan_beichuan_railway",
    "TOD_sichuan_hualian_steel",
    "TOD_sichuan_sanxia_textile",
    "TOD_sichuan_chongqing_electric_steel",
)

FORBIDDEN_MIO_ARCHETYPES = (
    "generic_tank_organization",
    "generic_motorized_mechanized_organization",
    "generic_general_aircraft_organization",
    "generic_battle_line_ship_organization",
)


def main() -> int:
    failures: list[str] = []
    for path in (MIO_FILE, CONCERN_FILE, LOCALISATION):
        if not path.exists():
            failures.append(f"missing {path.relative_to(ROOT)}")
    if failures:
        print("\n".join(failures))
        return 1

    mio_text = MIO_FILE.read_text(encoding="utf-8-sig")
    concern_text = CONCERN_FILE.read_text(encoding="utf-8-sig")
    for mio_id, (state_id, archetype) in MIO_CONTRACT.items():
        try:
            block = named_block(mio_text, mio_id)
        except ValueError:
            failures.append(f"missing MIO {mio_id}")
            continue
        for required in (f"include = {archetype}", "tag = SIC", "tag = SCG", f"controls_state = {state_id}"):
            if required not in block:
                failures.append(f"{mio_id}: missing {required}")
    for forbidden in FORBIDDEN_MIO_ARCHETYPES:
        if forbidden in mio_text:
            failures.append(f"unsupported Sichuan MIO archetype {forbidden}")

    for concern_id, state_id in CONCERN_CONTRACT.items():
        try:
            block = named_block(concern_text, concern_id)
        except ValueError:
            failures.append(f"missing concern {concern_id}")
            continue
        for required in ("original_tag = SIC", "original_tag = SCG", f"controls_state = {state_id}"):
            if required not in block:
                failures.append(f"{concern_id}: missing {required}")
    for forbidden in FORBIDDEN_COMPANIES:
        if forbidden in concern_text:
            failures.append(f"forbidden standalone concern {forbidden}")

    keys, duplicates, malformed = localisation_keys(LOCALISATION)
    required_keys = set(MIO_CONTRACT) | set(CONCERN_CONTRACT)
    required_keys |= {f"{key}_desc" for key in CONCERN_CONTRACT}
    for key in sorted(required_keys - keys):
        failures.append(f"missing localization {key}")
    failures.extend(f"duplicate localization {item}" for item in duplicates)
    failures.extend(f"malformed localization {item}" for item in malformed)

    if failures:
        print("\n".join(failures))
        return 1
    print("Sichuan enterprise contracts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the validator and confirm the expected failure**

Run:

```powershell
python tests/validate_sichuan_enterprises.py
```

Expected: exit code 1 with missing-file messages for the MIO, concern, and localization files.

---

### Task 2: Add the four shared industrial concerns

**Files:**
- Create: `common/ideas/SIC_SCG_companies.txt`
- Create: `localisation/simp_chinese/TOD_SIC_SCG_companies_l_simp_chinese.yml`

**Interfaces:**
- Consumes: state IDs 830 and 831; existing focuses `SIC_tianfuzhizhi`, `SCG_zuzhigonghui`, and `SCG_lianhezhengfu`.
- Produces: four `industrial_concern` IDs used unchanged by both countries.

- [ ] **Step 1: Create the shared advisor category**

Create `common/ideas/SIC_SCG_companies.txt` with `ideas = { industrial_concern = { ... } }` and these exact definitions:

| ID | Picture | Availability | Research | Modifier |
|---|---|---|---|---|
| `TOD_sichuan_minsheng_industry` | `generic_industrial_concern_1` | control 830; SIC completed `SIC_tianfuzhizhi` or SCG completed `SCG_lianhezhengfu` | `industry = 0.10` | infrastructure +10%, railway +10%, consumer goods −3% |
| `TOD_sichuan_huaxi_industry` | `generic_industrial_concern_1` | control 831; SIC completed `SIC_tianfuzhizhi` or SCG completed `SCG_zuzhigonghui` | `construction_tech = 0.10` | civilian factory construction +10%, military factory construction +5% |
| `TOD_sichuan_chongqing_electric` | `generic_industrial_concern_1` | control 830; SIC completed `SIC_tianfuzhizhi` or SCG completed `SCG_lianhezhengfu` | `electronics = 0.10` | research speed +3%, production efficiency growth +5% |
| `TOD_sichuan_tianfu_coal` | `generic_industrial_concern_1` | control 830; SIC completed `SIC_tianfuzhizhi` or SCG completed `SCG_lianhezhengfu` | `excavation_tech = 0.10` | local resources +15%, infrastructure construction +5% |

Every definition must use this shared-country and control pattern:

```hoi4
allowed = {
    OR = {
        original_tag = SIC
        original_tag = SCG
    }
}
available = {
    controls_state = 830
    OR = {
        has_completed_focus = SIC_tianfuzhizhi
        has_completed_focus = SCG_lianhezhengfu
    }
}
traits = { industrial_concern }
ai_will_do = { factor = 10 }
```

Use `Electronics_concern` instead of `industrial_concern` only for `TOD_sichuan_chongqing_electric`.

- [ ] **Step 2: Add the four historical names and descriptions**

Create the localization file with UTF-8 BOM and header `l_simp_chinese:`. Use these exact display names:

```yaml
 TOD_sichuan_minsheng_industry:0 "民生实业股份有限公司"
 TOD_sichuan_huaxi_industry:0 "华西兴业股份有限公司"
 TOD_sichuan_chongqing_electric:0 "重庆电力股份有限公司"
 TOD_sichuan_tianfu_coal:0 "天府煤矿公司"
```

Add a 60—100 Chinese-character `_desc` for each company describing its pre-1936 business and gameplay specialization without mentioning later wartime relocation.

- [ ] **Step 3: Run the validator**

Run `python tests/validate_sichuan_enterprises.py`.

Expected: concern checks pass; the command still fails because the MIO file is missing.

---

### Task 3: Add the five shared military industrial organizations

**Files:**
- Create: `common/military_industrial_organization/organizations/SIC_SCG_organization.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_SCG_companies_l_simp_chinese.yml`

**Interfaces:**
- Consumes: generic organization archetypes from `00_generic_organization.txt`, state IDs 830/831, and existing focus IDs listed below.
- Produces: five MIO IDs for later SIC Wubei focus rewards and SCG economy/military route interactions.

- [ ] **Step 1: Create all five organizations**

Use top-level named organization blocks. Every block must contain:

```hoi4
allowed = {
    OR = {
        tag = SIC
        tag = SCG
    }
}
available = {
    owner = {
        controls_state = 831
        OR = {
            has_completed_focus = SIC_baozhengjungong
            has_completed_focus = SCG_renminjundui
        }
    }
}
```

Create the exact mapping:

| ID | Include | Icon | State |
|---|---|---|---:|
| `TOD_sichuan_chengdu_arsenal_organization` | `generic_infantry_equipment_organization` | `GFX_idea_generic_infantry_equipment_manufacturer_2` | 831 |
| `TOD_sichuan_chongqing_weapon_repair_organization` | `generic_artillery_organization` | `GFX_idea_generic_artillery_manufacturer_2` | 830 |
| `TOD_sichuan_chuankang_ammunition_organization` | `generic_infantry_equipment_organization` | `GFX_idea_generic_infantry_equipment_manufacturer_2` | 831 |
| `TOD_sichuan_huaxing_machine_organization` | `generic_infantry_equipment_organization` | `GFX_idea_generic_infantry_equipment_manufacturer_2` | 831 |
| `TOD_sichuan_telecom_repair_organization` | `generic_support_equipment_organization` | `GFX_idea_generic_infantry_equipment_manufacturer_1` | 830 |

For each block, replace the state in `controls_state` with the table value. Do not add explicit tank, motorized, aircraft, or ship equipment types.

- [ ] **Step 2: Add one historical specialization trait to each organization**

Add one `add_trait` at `position = { x = 9 y = 0 }`, with `special_trait_background = yes` and the following exact effects:

| Trait token | Organization | Availability | Effects |
|---|---|---|---|
| `TOD_sichuan_mio_trait_chuanzao_standardization` | 成都兵工厂 | SIC `SIC_sichuan_moshi` or SCG `SCG_shixingjihuajingji` | reliability +10%, production efficiency gain +5% |
| `TOD_sichuan_mio_trait_frontline_repair` | 重庆武器修理所 | SIC `SIC_baozhengjungong` or SCG `SCG_junduizhuanyehua` | reliability +12%, resource need −5% |
| `TOD_sichuan_mio_trait_ammunition_mass_output` | 川康子弹厂 | SIC `SIC_zhengfudingdan` or SCG `SCG_shixingjihuajingji` | build cost −5%, production efficiency cap +5% |
| `TOD_sichuan_mio_trait_huaxing_light_machine_guns` | 华兴机器厂 | SIC `SIC_baozhengjungong` or SCG `SCG_yizhiqusheng` | soft attack +5%, reliability +5% |
| `TOD_sichuan_mio_trait_field_radio_network` | 电信机械修造厂 | SIC `SIC_baozhengjungong` or SCG `SCG_chongzugemingjundui` | reliability +10%, MIO research bonus +5% |

Use this availability structure in every trait:

```hoi4
available = {
    FROM = {
        OR = {
            has_completed_focus = SIC_sichuan_moshi
            has_completed_focus = SCG_shixingjihuajingji
        }
    }
}
```

Use `equipment_bonus` for reliability, build cost, and soft attack; use `production_bonus` for efficiency and resource need; use `organization_modifier` for the research bonus.

- [ ] **Step 3: Add MIO and trait localization**

Add the exact organization names:

```yaml
 TOD_sichuan_chengdu_arsenal_organization:0 "成都兵工厂"
 TOD_sichuan_chongqing_weapon_repair_organization:0 "重庆武器修理所"
 TOD_sichuan_chuankang_ammunition_organization:0 "川康绥靖公署子弹厂"
 TOD_sichuan_huaxing_machine_organization:0 "华西兴业公司华兴机器厂"
 TOD_sichuan_telecom_repair_organization:0 "军政部电信机械修造厂"
```

Add localization for all five trait tokens. Each trait description must state the historical production emphasis and the displayed bonus.

- [ ] **Step 4: Run the enterprise validator**

Run `python tests/validate_sichuan_enterprises.py`.

Expected: `Sichuan enterprise contracts validated` and exit code 0.

---

### Task 4: Add enterprise files to the existing Sichuan regression suite

**Files:**
- Modify: `tests/validate_sic_scg_constitutional_routes.py`

**Interfaces:**
- Consumes: the new company and MIO files.
- Produces: brace-balance and protected-content coverage in the main Sichuan validation command.

- [ ] **Step 1: Register the new Clausewitz files**

Add these paths to `CLAUSEWITZ_FILES`:

```python
ROOT / "common/ideas/SIC_SCG_companies.txt",
ROOT / "common/military_industrial_organization/organizations/SIC_SCG_organization.txt",
```

- [ ] **Step 2: Run both static validation commands**

Run:

```powershell
python tests/validate_sichuan_enterprises.py
python tests/validate_sic_scg_constitutional_routes.py
```

Expected: both exit 0; the protected SIC crisis and SCG uprising hashes remain unchanged.

- [ ] **Step 3: Inspect the game log after one launch**

Launch the mod once to the country-selection screen, exit, then search `HOI4_LOG.txt` for the nine new IDs and for `error` lines mentioning either new file.

Expected: every organization and concern loads; no unknown equipment type, invalid idea category, missing sprite, or missing localization error is attributed to the new files.
