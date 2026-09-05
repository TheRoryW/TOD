"""Validate country-specific equipment names for the Ming civil-war factions."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MING_FILE = ROOT / "localisation" / "simp_chinese" / "TOD_Ming_l_simp_chinese.yml"
MING_SUCCESSOR_FILES = {
    "XBJ": ROOT / "localisation" / "simp_chinese" / "TOD_XBJ_Northwest_Army_l_simp_chinese.yml",
    "GPS": ROOT / "localisation" / "simp_chinese" / "TOD_GPS_l_simp_chinese.yml",
    "SIC": ROOT / "localisation" / "simp_chinese" / "TOD_SIC_l_simp_chinese.yml",
    "XIN": ROOT / "localisation" / "simp_chinese" / "TOD_XIN_l_simp_chinese.yml",
    "MOB": ROOT / "localisation" / "simp_chinese" / "TOD_Mobei_l_simp_chinese.yml",
    "STG": ROOT / "localisation" / "simp_chinese" / "TOD_STG_l_simp_chinese.yml",
    "GOS": ROOT / "localisation" / "simp_chinese" / "TOD_GOS_l_simp_chinese.yml",
}
SRC_FILE = ROOT / "localisation" / "simp_chinese" / "TOD_SRC_l_simp_chinese.yml"
SCG_FILE = ROOT / "localisation" / "simp_chinese" / "TOD_SCG_l_simp_chinese.yml"
ROC_FILE = ROOT / "localisation" / "simp_chinese" / "TOD_ROC_l_simp_chinese.yml"
RED_ARMY_TAG = "SRC"
SICHUAN_RED_ARMY_TAG = "SCG"
REPUBLICAN_ARMY_TAG = "ROC"


def localisation_entries(path: Path, tag: str) -> dict[str, str]:
    """Return all simple localisation entries belonging to a country tag."""
    if not path.exists():
        return {}
    pattern = re.compile(rf"^\s*{tag}_(?P<key>[^:]+):\d*\s*\"(?P<value>.*)\"\s*$")
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.match(line)
        if match:
            entries[match.group("key")] = match.group("value")
    return entries


def is_equipment_name(key: str) -> bool:
    """Keep only country-specific names the equipment UI can resolve."""
    return any(
        marker in key
        for marker in ("equipment", "_chassis", "_hull", "_airframe", "infantry_weapons", "infantry_at")
    )


def main() -> int:
    failures: list[str] = []
    ming_equipment = {
        key: value
        for key, value in localisation_entries(MING_FILE, "MNG").items()
        if is_equipment_name(key)
    }
    if len(ming_equipment) < 250:
        failures.append("MNG source equipment-name catalogue is unexpectedly incomplete")

    for tag, path in MING_SUCCESSOR_FILES.items():
        entries = localisation_entries(path, tag)
        missing = sorted(set(ming_equipment) - set(entries))
        wrong = sorted(key for key in ming_equipment if entries.get(key) != ming_equipment[key])
        if missing:
            failures.append(f"{tag}: missing {len(missing)} Ming equipment names")
        if wrong:
            failures.append(f"{tag}: {len(wrong)} equipment names differ from MNG")

    src = {
        key: value
        for key, value in localisation_entries(SRC_FILE, RED_ARMY_TAG).items()
        if is_equipment_name(key)
    }
    scg = {
        key: value
        for key, value in localisation_entries(SCG_FILE, SICHUAN_RED_ARMY_TAG).items()
        if is_equipment_name(key)
    }
    roc = {
        key: value
        for key, value in localisation_entries(ROC_FILE, REPUBLICAN_ARMY_TAG).items()
        if is_equipment_name(key)
    }
    required_red_keys = {
        "infantry_equipment_0",
        "infantry_equipment_3",
        "motorized_equipment_1",
        "mechanized_equipment_3",
        "armored_car_equipment_2",
    }
    missing_src = sorted(required_red_keys - set(src))
    if missing_src:
        failures.append(f"SRC: missing restored Northeast Red Army names: {', '.join(missing_src)}")
    if "辽阳" not in src.get("infantry_equipment_0", ""):
        failures.append("SRC: original Liaoyang arsenal naming was not restored")

    if src != scg:
        failures.append("SCG: Sichuan Red Army must use the same equipment names as SRC")
    if set(roc) != set(src):
        failures.append("ROC: Republican Army must cover the same equipment keys as SRC")
    if any("红军" in value or "辽阳" in value for value in roc.values()):
        failures.append("ROC: Republican Army names must be independent from Northeast Red Army names")
    if "共和军" not in "\n".join(roc.values()):
        failures.append("ROC: no Republican Army naming was added")

    if failures:
        print("FAIL")
        print("\n".join(failures))
        return 1

    print(
        "PASS: Ming successors inherit the Ming catalogue; "
        "SRC/SCG share Northeast Red Army names; ROC has its own naming."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
