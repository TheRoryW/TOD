"""Static contract for MNG's representative roster and shared Sichuan MIOs."""

from __future__ import annotations

import re
import sys

sys.path.insert(0, str(__file__.replace("validate_ming_sichuan_enterprises.py", "")))

from validate_sic_scg_constitutional_routes import ROOT, localisation_keys, named_block


MNG_COMPANIES = {
    "MNG_guojia_tielu_zongju": "industrial_concern",
    "MNG_shuntian_jianshe_zonggongshu": "industrial_concern",
    "MNG_dongbei_gongye_jituan": "industrial_concern",
    "MNG_hanjiang_youse_jituan": "industrial_concern",
    "MNG_yangzi_dianqihua_kaifaju": "electronics_concern",
}

MNG_MIOS = {
    "MNG_qiantang_engineering_organization": "generic_infantry_tank_organization",
    "MNG_wuyi_heavy_industry_organization": "generic_heavy_tank_organization",
    "MNG_changjiang_arms_organization": "generic_infantry_equipment_organization",
    "MNG_luoyang_ordnance_organization": "generic_artillery_organization",
    "MNG_tangshan_heavy_machine_organization": "generic_motorized_mechanized_organization",
    "MNG_baoding_aircraft_organization": "generic_cas_aircraft_organization",
    "MNG_kaifeng_aviation_organization": "generic_medium_aircraft_organization",
    "MNG_datong_heavy_aircraft_organization": "generic_heavy_aircraft_organization",
    "MNG_jiangnan_naval_repair_organization": "generic_task_force_ship_organization",
    "MNG_fuzhou_shipyard_organization": "generic_submarine_organization",
}

SICHUAN_MIOS = {
    "TOD_sichuan_chengdu_arsenal_organization": (831, "generic_infantry_equipment_organization"),
    "TOD_sichuan_chongqing_ammunition_organization": (830, "generic_support_equipment_organization"),
    "TOD_sichuan_huaxing_machine_organization": (830, "generic_infantry_equipment_organization"),
    "TOD_sichuan_chongqing_weapon_repair_organization": (830, "generic_artillery_organization"),
    "TOD_sichuan_beichuan_railway_organization": (830, "generic_motorized_mechanized_organization"),
    "TOD_sichuan_minsheng_machine_works_organization": (830, "generic_raider_ship_organization"),
    "TOD_sichuan_zhonghua_shipyard_organization": (830, "generic_escort_ship_organization"),
}

RETIRED_SICHUAN_MIOS = {
    "TOD_sichuan_chuankang_ammunition_organization",
    "TOD_sichuan_telecom_repair_organization",
}


def main() -> int:
    failures: list[str] = []
    mng_company_path = ROOT / "common/ideas/MNG_companies.txt"
    mng_mio_path = ROOT / "common/military_industrial_organization/organizations/MNG_organization.txt"
    mng_localisation_path = ROOT / "localisation/simp_chinese/TOD_Ming_l_simp_chinese.yml"
    ming_civil_war_path = ROOT / "events/mingcivwar.txt"
    stg_release_effect_path = ROOT / "common/scripted_effects/damingneizhanyong.txt"
    shuntian_focus_path = ROOT / "common/national_focus/shuntianzhengfu.txt"
    louisiana_focus_path = ROOT / "common/national_focus/Louisiana.txt"
    louisiana_ideas_path = ROOT / "common/ideas/Louisiana_ideas.txt"
    louisiana_localisation_paths = (
        ROOT / "localisation/simp_chinese/TOD_Louisiana_l_simp_chinese.yml",
        ROOT / "localisation/english/TOD_Louisiana_l_english.yml",
    )
    sichuan_mio_path = ROOT / "common/military_industrial_organization/organizations/SIC_SCG_organization.txt"
    sichuan_localisation_path = ROOT / "localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml"
    retired_localisation_paths = (
        ROOT / "localisation/simp_chinese/TOD_MNG_companies_l_simp_chinese.yml",
        ROOT / "localisation/simp_chinese/TOD_SIC_SCG_companies_l_simp_chinese.yml",
    )

    for path in (
        mng_company_path,
        mng_mio_path,
        mng_localisation_path,
        ming_civil_war_path,
        stg_release_effect_path,
        shuntian_focus_path,
        louisiana_focus_path,
        louisiana_ideas_path,
        *louisiana_localisation_paths,
        sichuan_mio_path,
        sichuan_localisation_path,
    ):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")
    if failures:
        print("Ming and Sichuan enterprise validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1

    for localisation_path in retired_localisation_paths:
        if localisation_path.exists():
            failures.append(f"standalone localisation must be merged: {localisation_path.name}")

    mng_company_text = mng_company_path.read_text(encoding="utf-8-sig")
    mng_mio_text = mng_mio_path.read_text(encoding="utf-8-sig")
    ming_civil_war_text = ming_civil_war_path.read_text(encoding="utf-8-sig")
    stg_release_effect_text = stg_release_effect_path.read_text(encoding="utf-8-sig")
    shuntian_focus_text = shuntian_focus_path.read_text(encoding="utf-8-sig")
    louisiana_focus_text = louisiana_focus_path.read_text(encoding="utf-8-sig")
    louisiana_ideas_text = louisiana_ideas_path.read_text(encoding="utf-8-sig")
    sichuan_mio_text = sichuan_mio_path.read_text(encoding="utf-8-sig")

    for idea_id in ("FRL_citizens_rights_idea", "FRL_dispel_injustice_idea"):
        if f"add_ideas = {idea_id}" not in louisiana_focus_text:
            failures.append(f"Louisiana focus tree: missing intended {idea_id} reward")
        else:
            try:
                named_block(louisiana_ideas_text, idea_id)
            except ValueError:
                failures.append(f"Louisiana focus tree: {idea_id} reward has no idea definition")
    for localisation_path in louisiana_localisation_paths:
        keys, _, _ = localisation_keys(localisation_path)
        for idea_id in ("FRL_citizens_rights_idea", "FRL_dispel_injustice_idea"):
            for key in (idea_id, f"{idea_id}_desc"):
                if key not in keys:
                    failures.append(f"{localisation_path.name}: missing {key}")
    if "add_ideas = FRL_end_invisible_persecution" in louisiana_focus_text:
        failures.append("Louisiana focus tree: FRL_end_invisible_persecution is a focus ID, not an idea ID")

    if re.search(r"(?m)^\s*retire_character\s*=\s*MNG_2_zzx\s*$", ming_civil_war_text):
        failures.append("mingcivwar.txt: MNG_2_zzx is already retired at game start and must not be retired again")

    try:
        stg_release_block = named_block(stg_release_effect_text, "MNG_release_STG")
    except ValueError:
        failures.append("MNG_release_STG: missing scripted release effect")
    else:
        stg_create = stg_release_block.find("release = STG")
        stg_transfer = stg_release_block.find("every_owned_state")
        if "NOT = { country_exists = STG }" not in stg_release_block or stg_create < 0:
            failures.append("MNG_release_STG: must create STG before transferring its stockpile")
        elif stg_transfer < 0 or stg_create > stg_transfer:
            failures.append("MNG_release_STG: STG must be created before its core states are transferred")

    if "load_oob = shuntian_zhuangjia" in shuntian_focus_text:
        failures.append("shuntianzhengfu.txt: STG focus loads missing shuntian_zhuangjia OOB")

    unit_transfer_blocks = re.findall(
        r"transfer_units_fraction\s*=\s*\{\s*"
        r"target\s*=\s*([A-Z0-9_]+)\s*"
        r"stockpile_ratio\s*=\s*([0-9.]+)\s*"
        r"army_ratio\s*=\s*([0-9.]+)\s*"
        r"navy_ratio\s*=\s*([0-9.]+)\s*"
        r"air_ratio\s*=\s*([0-9.]+)",
        ming_civil_war_text,
    )
    if len(unit_transfer_blocks) != 20:
        failures.append(f"mingcivwar.txt: expected 20 stockpile-only transfer blocks, found {len(unit_transfer_blocks)}")
    if re.search(r"\bsize\s*=", ming_civil_war_text):
        failures.append("mingcivwar.txt: regional releases must not transfer Ming field units via size")
    for target, stockpile_text, army_text, navy_text, air_text in unit_transfer_blocks:
        stockpile_ratio = float(stockpile_text)
        if stockpile_ratio <= 0:
            failures.append(f"mingcivwar.txt: {target} receives no equipment stockpile")
        for unit_type, ratio_text in (("army", army_text), ("navy", navy_text), ("air", air_text)):
            if float(ratio_text) != 0:
                failures.append(f"mingcivwar.txt: {target} still transfers {unit_type} units (ratio = {ratio_text})")

    character_text = "\n".join(
        path.read_text(encoding="utf-8-sig")
        for path in (ROOT / "common/characters").glob("*.txt")
    )
    retired_characters = sorted(set(re.findall(r"(?m)^\s*retire_character\s*=\s*(MNG_[A-Za-z0-9_]+)", ming_civil_war_text)))
    for character_id in retired_characters:
        if not re.search(rf"(?m)^\s*{re.escape(character_id)}\s*=\s*\{{", character_text):
            failures.append(f"mingcivwar.txt: retires undefined character {character_id}")

    stg_transfer = ming_civil_war_text.find("target = STG")
    stg_release = ming_civil_war_text.find("MNG_release_STG = yes")
    if stg_transfer < 0 or stg_release < 0 or stg_transfer < stg_release:
        failures.append("mingcivwar.txt: STG receives equipment before it is released")
    for company_id, concern_type in MNG_COMPANIES.items():
        try:
            block = named_block(mng_company_text, company_id)
        except ValueError as error:
            failures.append(str(error))
            continue
        for required in ("original_tag = MNG", concern_type):
            if required not in block:
                failures.append(f"{company_id}: missing {required}")

    for mio_id, archetype in MNG_MIOS.items():
        try:
            block = named_block(mng_mio_text, mio_id)
        except ValueError as error:
            failures.append(str(error))
            continue
        for required in ("tag = MNG", f"include = {archetype}"):
            if required not in block:
                failures.append(f"{mio_id}: missing {required}")

    for mio_id, (state, archetype) in SICHUAN_MIOS.items():
        try:
            block = named_block(sichuan_mio_text, mio_id)
        except ValueError as error:
            failures.append(str(error))
            continue
        for required in (
            "tag = SIC",
            "tag = SCG",
            "original_tag = SIC",
            "original_tag = SCG",
            f"controls_state = {state}",
            f"include = {archetype}",
        ):
            if required not in block:
                failures.append(f"{mio_id}: missing {required}")
    for retired_id in RETIRED_SICHUAN_MIOS:
        if retired_id in sichuan_mio_text:
            failures.append(f"retired Sichuan MIO remains: {retired_id}")

    for localisation_path, identifiers in (
        (mng_localisation_path, (*MNG_COMPANIES, *MNG_MIOS)),
        (sichuan_localisation_path, SICHUAN_MIOS),
    ):
        if not localisation_path.read_bytes().startswith(b"\xef\xbb\xbf"):
            failures.append(f"{localisation_path.name}: missing UTF-8 BOM required by HOI4 localisation")
        keys, _, _ = localisation_keys(localisation_path)
        for identifier in identifiers:
            for key in (identifier, f"{identifier}_desc"):
                if key not in keys:
                    failures.append(f"{localisation_path.name}: missing {key}")

    if failures:
        print("Ming and Sichuan enterprise validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("Ming and Sichuan enterprise validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
