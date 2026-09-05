"""Validate the random commander name pools used by Ming and Chinese factions."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME_FILES = (
    ROOT / "common" / "names" / "TOD_missing_character_names.txt",
)
LEGACY_NAME_FILE = ROOT / "common" / "names" / "00_names.txt"
CUSTOM_NON_CHINESE_NAME_TAGS = ("INS_HOL",)

# These custom country tags can generate characters but previously had no
# country-name pool at all.  Keep the full trio of fields required by HOI4.
CUSTOM_GENERATED_CHARACTER_TAGS = (
    "ADE",
    "ALA",
    "BAV",
    "COE",
    "HDF",
    "HWH",
    "INA",
    "JOF",
    "LAB",
    "LAM",
    "LPC",
    "LSM",
    "MES",
    "MLJ",
    "NJE",
    "ROK",
    "ROS",
    "SHE",
    "UTS",
)

CHINESE_COMMANDER_TAGS = (
    "MNG",
    "XBJ",
    "GPS",
    "SRC",
    "SIC",
    "USC",
    "ROC",
    "GOS",
    "XIN",
    "MOB",
    "STG",
    "SCG",
)

# The document supplies 100 non-historical random division commander names.
EXPECTED_GIVEN_NAME_COUNT = 100
REFERENCE_GIVEN_NAMES = {"Wenxuan", "Zhiqiang", "Guodong", "Fuming", "Baoyuan"}
HISTORICAL_GIVEN_NAMES = {"Yujian", "Dingguo", "Kewang", "Nengqi", "Wenxiu", "Chenggong", "Yihai", "Tengjiao", "Guo", "Yaoqi"}
SRC_FOCUS_LOCKED_OFFICERS = (
    "SRC_sa_shijun",
    "SRC_deng_zhaoxiang",
    "SRC_yang_jingyu",
    "SRC_xu_xiangqian",
    "SRC_zhu_rui",
    "SRC_wang_yongqing",
    "SRC_wang_minjing",
)


def extract_braced_block(text: str, start: int) -> str:
    """Return the braced block beginning at ``start``."""
    opening = text.find("{", start)
    if opening < 0:
        raise ValueError("opening brace not found")
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[opening + 1 : index]
    raise ValueError("unclosed brace")


def named_block(text: str, name: str) -> str | None:
    match = re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*=\s*\{{", text)
    return None if match is None else extract_braced_block(text, match.start())


def token_list(block: str, key: str) -> list[str]:
    nested = named_block(block, key)
    if nested is None:
        return []
    return re.findall(r'"([^"]+)"|([^\s{}#]+)', nested) and [
        quoted or bare for quoted, bare in re.findall(r'"([^"]+)"|([^\s{}#]+)', nested)
    ]


def load_pools() -> dict[str, tuple[list[str], list[str]]]:
    content = "\n".join(path.read_text(encoding="utf-8") for path in NAME_FILES)
    pools: dict[str, tuple[list[str], list[str]]] = {}
    for tag in CHINESE_COMMANDER_TAGS:
        country = named_block(content, tag)
        if country is None:
            continue
        male = named_block(country, "male")
        if male is None:
            continue
        pools[tag] = (token_list(male, "names"), token_list(country, "surnames"))
    return pools


def main() -> int:
    pools = load_pools()
    failures: list[str] = []
    canonical: tuple[list[str], list[str]] | None = None

    if LEGACY_NAME_FILE.exists():
        failures.append("common/names/00_names.txt shadows the current base-game name pools")

    for tag in CHINESE_COMMANDER_TAGS:
        if tag not in pools:
            failures.append(f"{tag}: missing Chinese random commander name pool")
            continue

        given_names, surnames = pools[tag]
        if len(given_names) != EXPECTED_GIVEN_NAME_COUNT:
            failures.append(f"{tag}: expected {EXPECTED_GIVEN_NAME_COUNT} given names, found {len(given_names)}")
        if not REFERENCE_GIVEN_NAMES.issubset(given_names):
            failures.append(f"{tag}: missing names from the supplied reference list")
        if HISTORICAL_GIVEN_NAMES.intersection(given_names):
            failures.append(f"{tag}: historical commanders must not be generated randomly")
        if not surnames:
            failures.append(f"{tag}: surname pool is empty")

        if canonical is None:
            canonical = (given_names, surnames)
        elif (given_names, surnames) != canonical:
            failures.append(f"{tag}: pool differs from the shared Chinese commander pool")

    custom_name_text = "\n".join(path.read_text(encoding="utf-8") for path in NAME_FILES)
    custom_pool_tags = re.findall(r"(?m)^([A-Z0-9_]+)\s*=\s*\{", custom_name_text)
    for tag in custom_pool_tags:
        block = named_block(custom_name_text, tag)
        if block is None:
            failures.append(f"{tag}: custom name-pool block cannot be read")
            continue
        if named_block(block, "male") is None:
            failures.append(f"{tag}: custom country has no male generated-character name pool")
        if named_block(block, "female") is None:
            failures.append(f"{tag}: custom country has no female generated-character name pool")
        if not token_list(block, "surnames"):
            failures.append(f"{tag}: custom country has no generated-character surname pool")

    for tag in CUSTOM_NON_CHINESE_NAME_TAGS:
        block = named_block(custom_name_text, tag)
        if block is None or named_block(block, "male") is None or named_block(block, "female") is None or not token_list(block, "surnames"):
            failures.append(f"{tag}: custom name pool was not preserved outside the base-name override")

    for tag in CUSTOM_GENERATED_CHARACTER_TAGS:
        block = named_block(custom_name_text, tag)
        if block is None:
            failures.append(f"{tag}: generated characters have no country name pool")
            continue
        if named_block(block, "male") is None:
            failures.append(f"{tag}: generated characters have no male name pool")
        if named_block(block, "female") is None:
            failures.append(f"{tag}: generated characters have no female name pool")
        if not token_list(block, "surnames"):
            failures.append(f"{tag}: generated characters have no surname pool")

    src_history_text = (ROOT / "history/countries/SRC - hongjun.txt").read_text(encoding="utf-8-sig")
    src_character_text = (ROOT / "common/characters/SRC.txt").read_text(encoding="utf-8-sig")
    src_event_text = (ROOT / "events/SRC.txt").read_text(encoding="utf-8-sig")
    for character_id in SRC_FOCUS_LOCKED_OFFICERS:
        if re.search(rf"(?m)^\s*retire_character\s*=\s*{re.escape(character_id)}\s*$", src_history_text):
            failures.append(f"{character_id}: focus-gated officer is permanently retired at game start")
        character_block = named_block(src_character_text, character_id)
        if character_block is None:
            failures.append(f"{character_id}: missing character definition")
        elif re.search(r"(?m)^\s*(?:corps_commander|field_marshal|navy_leader)\s*=", character_block):
            failures.append(f"{character_id}: officer role is granted before its focus event")
        if not re.search(rf"(?m)^\s*character\s*=\s*{re.escape(character_id)}\s*$", src_event_text):
            failures.append(f"{character_id}: no focus event grants the officer role")
    if "add_country_leader_role" in src_event_text:
        failures.append("SRC leadership elections must promote existing leaders instead of duplicating country-leader roles")

    if failures:
        print("FAIL")
        print("\n".join(failures))
        return 1

    print(f"PASS: {len(CHINESE_COMMANDER_TAGS)} Chinese factions share the 100-name commander pool")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
