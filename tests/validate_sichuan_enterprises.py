"""Static contract for the shared pre-1936 Sichuan enterprises."""

from __future__ import annotations

import sys

sys.path.insert(0, str(__file__.replace("validate_sichuan_enterprises.py", "")))

from validate_sic_scg_constitutional_routes import ROOT, localisation_keys, named_block


COMPANIES = {
    "TOD_sichuan_minsheng_industry": (830, "industrial_concern"),
    "TOD_sichuan_huaxi_industry": (831, "industrial_concern"),
    "TOD_sichuan_chongqing_electric": (830, "electronics_concern"),
    "TOD_sichuan_tianfu_coal": (830, "industrial_concern"),
}

MIOS = {
    "TOD_sichuan_chengdu_arsenal_organization": (831, "generic_infantry_equipment_organization"),
    "TOD_sichuan_chongqing_weapon_repair_organization": (830, "generic_artillery_organization"),
    "TOD_sichuan_chongqing_ammunition_organization": (830, "generic_support_equipment_organization"),
    "TOD_sichuan_huaxing_machine_organization": (830, "generic_infantry_equipment_organization"),
    "TOD_sichuan_beichuan_railway_organization": (830, "generic_motorized_mechanized_organization"),
    "TOD_sichuan_minsheng_machine_works_organization": (830, "generic_raider_ship_organization"),
    "TOD_sichuan_zhonghua_shipyard_organization": (830, "generic_escort_ship_organization"),
}

FORBIDDEN_COMPANIES = {
    "TOD_sichuan_minsheng_machine",
    "TOD_sichuan_beichuan_railway",
    "TOD_sichuan_hualian_steel",
    "TOD_sichuan_sanxia_textile",
    "TOD_sichuan_chongqing_electric_steel",
}

RETIRED_MIOS = {
    "TOD_sichuan_chuankang_ammunition_organization",
    "TOD_sichuan_telecom_repair_organization",
}


def main() -> int:
    failures: list[str] = []
    company_path = ROOT / "common/ideas/SIC_SCG_companies.txt"
    mio_path = ROOT / "common/military_industrial_organization/organizations/SIC_SCG_organization.txt"
    localisation_path = ROOT / "localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml"

    for path in (company_path, mio_path, localisation_path):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")
    if failures:
        print("\n".join(failures))
        return 1

    if not localisation_path.read_bytes().startswith(b"\xef\xbb\xbf"):
        failures.append(f"{localisation_path.name}: missing UTF-8 BOM required by HOI4 localisation")

    company_text = company_path.read_text(encoding="utf-8-sig")
    mio_text = mio_path.read_text(encoding="utf-8-sig")
    for forbidden in FORBIDDEN_COMPANIES:
        if forbidden in company_text:
            failures.append(f"forbidden non-historical company is present: {forbidden}")
    for retired_mio in RETIRED_MIOS:
        if retired_mio in mio_text:
            failures.append(f"retired Sichuan MIO is present: {retired_mio}")

    for company_id, (state, concern_type) in COMPANIES.items():
        try:
            block = named_block(company_text, company_id)
        except ValueError as error:
            failures.append(str(error))
            continue
        for required in ("original_tag = SIC", "original_tag = SCG", f"controls_state = {state}", concern_type):
            if required not in block:
                failures.append(f"{company_id}: missing {required}")

    for mio_id, (state, archetype) in MIOS.items():
        try:
            block = named_block(mio_text, mio_id)
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
        try:
            availability = named_block(block, "available")
        except ValueError as error:
            failures.append(f"{mio_id}: {error}")
            continue
        if "has_completed_focus" in availability:
            failures.append(f"{mio_id}: institution availability is still locked behind a focus")

    keys, _, _ = localisation_keys(localisation_path)
    for identifier in (*COMPANIES, *MIOS):
        for key in (identifier, f"{identifier}_desc"):
            if key not in keys:
                failures.append(f"{localisation_path.name}: missing {key}")

    if failures:
        print("Sichuan enterprise validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("Sichuan enterprise validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
