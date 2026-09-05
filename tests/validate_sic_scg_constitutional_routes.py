"""Static contract checks for the Sichuan constitutional-route content.

This intentionally stays small: it checks the content identifiers that make the
two routes playable and catches unbalanced Clausewitz blocks before launching
the game.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PROTECTED_HASH_FIXTURE = ROOT / "tests/fixtures/sichuan_protected_opening_hashes.json"

SIC_FOCUS = ROOT / "common/national_focus/chuanyudifangsi.txt"
SCG_FOCUS = ROOT / "common/national_focus/sichuangemingzhengfu.txt"
SIC_LOCALISATION = ROOT / "localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml"
SCG_LOCALISATION = ROOT / "localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml"


def extract_blocks(content: str, keyword: str) -> list[str]:
    """Extract top-level Clausewitz blocks beginning with ``keyword = {``."""
    blocks: list[str] = []
    pattern = re.compile(rf"(?m)^\s*{re.escape(keyword)}\s*=\s*\{{")
    for match in pattern.finditer(content):
        brace = content.find("{", match.start())
        depth = 0
        for index in range(brace, len(content)):
            if content[index] == "{":
                depth += 1
            elif content[index] == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(content[match.start() : index + 1])
                    break
    return blocks


def block_value(block: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*([^\s#}}]+)", block)
    return match.group(1) if match else None


def event_block(content: str, event_id: str) -> str:
    for keyword in ("country_event", "news_event"):
        for block in extract_blocks(content, keyword):
            if block_value(block, "id") == event_id:
                return block
    raise ValueError(f"missing event block {event_id}")


def named_block(content: str, block_id: str) -> str:
    """Extract a named Clausewitz block such as a character definition."""
    pattern = re.compile(rf"(?m)^\s*{re.escape(block_id)}\s*=\s*\{{")
    match = pattern.search(content)
    if not match:
        raise ValueError(f"missing named block {block_id}")
    brace = content.find("{", match.start())
    depth = 0
    for index in range(brace, len(content)):
        if content[index] == "{":
            depth += 1
        elif content[index] == "}":
            depth -= 1
            if depth == 0:
                return content[match.start() : index + 1]
    raise ValueError(f"unbalanced named block {block_id}")


def protected_sections() -> dict[str, str]:
    sic_focus = SIC_FOCUS.read_text(encoding="utf-8-sig")
    scg_focus = SCG_FOCUS.read_text(encoding="utf-8-sig")
    events = (ROOT / "events/SiChuan.txt").read_text(encoding="utf-8-sig")
    sic_opening = sic_focus.split("# 清政系宪政试验", 1)[0]
    # Narrative-only hooks requested for four legacy milestones are validated
    # separately below; ignore only those exact lines when guarding gameplay.
    sic_opening = re.sub(
        r"^\s*country_event = \{ id = TODSIC\.(?:1013|1014|1015|1016) days = 1 \}\r?\n",
        "",
        sic_opening,
        flags=re.M,
    )
    scg_opening = scg_focus.split("#革命成功", 1)[0]
    scg_opening = re.sub(
        r"^\s*country_event = \{ id = TODSIC\.(?:1065|1066|1067) days = 1 \}\r?\n",
        "",
        scg_opening,
        flags=re.M,
    )
    return {
        "sic_focus_opening": sic_opening,
        "scg_focus_civil_war": scg_opening,
        "sic_crisis_decisions": (ROOT / "common/decisions/SIC.txt").read_text(encoding="utf-8-sig"),
        "scg_uprising_decisions": (ROOT / "common/decisions/SCG.txt").read_text(encoding="utf-8-sig"),
        "scg_victory_event": event_block(events, "TODSIC.1005"),
    }


def section_hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256(text.encode("utf-8")).hexdigest()
        for name, text in protected_sections().items()
    }


def localisation_keys(path: Path) -> tuple[set[str], list[str], list[str]]:
    keys: set[str] = set()
    duplicates: list[str] = []
    malformed_quotes: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        match = re.match(r"\s*([^\s:#]+):", line)
        if match:
            key = match.group(1)
            if key in keys:
                duplicates.append(f"{key} at line {line_number}")
            keys.add(key)
        if '"' in line and line.count('"') % 2:
            malformed_quotes.append(f"line {line_number}: {line.strip()}")
    return keys, duplicates, malformed_quotes


def focus_records(path: Path) -> dict[str, dict[str, object]]:
    records: dict[str, dict[str, object]] = {}
    for block in extract_blocks(path.read_text(encoding="utf-8-sig"), "focus"):
        focus_id = block_value(block, "id")
        if not focus_id:
            continue
        prerequisites = [
            prerequisite
            for prerequisite_block in re.findall(
                r"prerequisite\s*=\s*\{([^}]*)\}", block, re.S
            )
            for prerequisite in re.findall(
                r"focus\s*=\s*([^\s#}]+)", prerequisite_block
            )
        ]
        records[focus_id] = {
            "block": block,
            "x": int(block_value(block, "x") or 0),
            "y": int(block_value(block, "y") or 0),
            "cost": int(block_value(block, "cost") or 0),
            "prerequisites": prerequisites,
            "icon": block_value(block, "icon"),
        }
    return records


def scg_phase(focus_id: str, block: str) -> str:
    if (
        "has_country_flag = SCG_gemingchenggong" in block
        and "NOT =" in block
    ):
        return "civil_war"
    return "postwar"


def validate_focus_graph(label: str, path: Path, failures: list[str]) -> None:
    records = focus_records(path)
    coordinates: dict[tuple[str, int, int], list[str]] = {}
    for focus_id, record in records.items():
        phase = scg_phase(focus_id, str(record["block"])) if label == "SCG" else "all"
        key = (phase, int(record["x"]), int(record["y"]))
        coordinates.setdefault(key, []).append(focus_id)
        for prerequisite in record["prerequisites"]:
            if prerequisite not in records:
                failures.append(f"{label} focus {focus_id}: missing prerequisite {prerequisite}")
                continue
            prerequisite_record = records[prerequisite]
            prerequisite_phase = (
                scg_phase(prerequisite, str(prerequisite_record["block"]))
                if label == "SCG"
                else "all"
            )
            if phase == prerequisite_phase and int(record["y"]) <= int(prerequisite_record["y"]):
                failures.append(
                    f"{label} focus edge is not downward: {prerequisite} "
                    f"({prerequisite_record['y']}) -> {focus_id} ({record['y']})"
                )
    for (phase, x, y), focus_ids in coordinates.items():
        if len(focus_ids) > 1:
            failures.append(
                f"{label} duplicate same-phase coordinate {phase} ({x},{y}): {', '.join(focus_ids)}"
            )


def validate_focus_localisation(path: Path, localisation: Path, failures: list[str]) -> None:
    keys, duplicates, malformed_quotes = localisation_keys(localisation)
    if localisation == SIC_LOCALISATION:
        # The shared MNG equipment-name import intentionally finishes with
        # three scout-plane overrides; they are unrelated to focus text.
        equipment_overrides = {
            "SIC_scout_plane_equipment_0",
            "SIC_scout_plane_equipment_0_short",
            "SIC_scout_plane_equipment_1_short",
        }
        duplicates = [
            duplicate
            for duplicate in duplicates
            if duplicate.split(" at line", 1)[0] not in equipment_overrides
        ]
    for focus_id in focus_records(path):
        for required_key in (focus_id, f"{focus_id}_desc"):
            if required_key not in keys:
                failures.append(f"{localisation.name}: missing {required_key}")
    failures.extend(f"{localisation.name}: duplicate {item}" for item in duplicates)
    failures.extend(f"{localisation.name}: malformed quote {item}" for item in malformed_quotes)


def validate_custom_focus_sprites(path: Path, failures: list[str]) -> None:
    interface_text = "\n".join(
        file.read_text(encoding="utf-8-sig", errors="ignore")
        for file in (ROOT / "interface").glob("*.gfx")
    )
    sprite_textures = dict(
        re.findall(
            r'name\s*=\s*"([^\"]+)"[\s\S]*?texturefile\s*=\s*"([^\"]+)"',
            interface_text,
        )
    )
    for focus_id, record in focus_records(path).items():
        icon = record["icon"]
        if not isinstance(icon, str) or not icon.startswith(("GFX_SIC_", "GFX_SCG_")):
            continue
        texture = sprite_textures.get(icon)
        if not texture:
            failures.append(f"{focus_id}: missing sprite definition {icon}")
        elif not (ROOT / texture).exists():
            failures.append(f"{focus_id}: missing sprite texture {texture}")


def validate_postwar_ai(path: Path, marker: str, failures: list[str]) -> None:
    content = path.read_text(encoding="utf-8-sig")
    postwar = content.split(marker, 1)[-1]
    for block in extract_blocks(postwar, "focus"):
        focus_id = block_value(block, "id") or "unknown"
        if re.search(r"ai_will_do\s*=\s*\{\s*factor\s*=\s*0\s*\}", block, re.S):
            failures.append(f"{focus_id}: postwar focus has zero AI weight")

TEXT_REQUIREMENTS = {
    "SIC constitutional focuses": (
        ROOT / "common/national_focus/chuanyudifangsi.txt",
        (
            "SIC_qingzhengxi_sichuan",
            "SIC_sichuan_jibenfa",
            "SIC_zerenneige",
            "SIC_sichuan_moshi",
            "SIC_xianzheng_jiuguo_xuanyan",
            "SIC_quanguo_zhixianpai_dahui",
            "SIC_daming_lixian_guo",
        ),
    ),
    "SCG bicameral focuses": (
        ROOT / "common/national_focus/sichuangemingzhengfu.txt",
        (
            "SCG_geminghou_diyici_huiyi",
            "SCG_duodang_shehuizhuyi",
            "SCG_jianli_renmin_dahui",
            "SCG_jianli_zhengdanghui",
            "SCG_liangyuan_yishi_guize",
            "SCG_sichuan_shehuizhuyi_xianfa",
            "SCG_zhonghua_shehuizhuyi_gongheguo",
        ),
    ),
    "SIC decision categories": (
        ROOT / "common/decisions/categories/SIC_constitutional_reform.txt",
        ("SIC_qingzhengxi_gaige_categories", "SIC_xianzhengtongyi_categories"),
    ),
    "SCG decision categories": (
        ROOT / "common/decisions/categories/SCG_bicameral_politics.txt",
        (
            "SCG_liangyuan_zhengzhi_categories",
            "SCG_chongjian_categories",
            "SCG_quanguo_geming_categories",
        ),
    ),
    "SIC decisions": (
        ROOT / "common/decisions/SIC_constitutional_reform.txt",
        (
            "SIC_kaizhan_shehui_diaocha",
            "SIC_gongbu_xinzheng_baipishu",
            "SIC_zhichi_quanguo_zhixianpai",
            "SIC_zhaokai_quanguo_xianzheng_xuanchuan",
        ),
    ),
    "SCG decisions": (
        ROOT / "common/decisions/SCG_bicameral_politics.txt",
        ("SCG_zhaokai_renmin_dahui", "SCG_huifu_chengdu_gongchang"),
    ),
    "SIC modifiers and spirits": (
        ROOT / "common/dynamic_modifiers/TOD_SIC_modifiers.txt",
        ("SIC_qingzhengxi_shiyan",),
    ),
    "SCG modifiers and spirits": (
        ROOT / "common/dynamic_modifiers/TOD_SCG_modifiers.txt",
        ("SCG_liangyuan_zhengzhi",),
    ),
    "SIC ideas": (
        ROOT / "common/ideas/SIC_idea.txt",
        (
            "SIC_jundui_tuichu_zhengzhi",
            "SIC_sichuan_jibenfa_idea",
            "SIC_zeren_neige_idea",
            "SIC_xianfa_guominjun",
            "SIC_xianzheng_tongyi_dongyuan",
            "SIC_gongkai_caizheng",
            "SIC_laogong_ziben_xieshang",
            "SIC_quanguo_tongyi_shichang",
            "SIC_quanguo_xianzheng_gangyao",
            "SIC_xianzheng_chenggong",
            "SIC_daming_lixian_guo",
        ),
    ),
    "SCG ideas": (
        ROOT / "common/ideas/SCG_idea.txt",
        ("SCG_liangyuan_xietiao", "SCG_zhonghua_shehuizhuyi_gongheguo"),
    ),
    "SCG bicameral updater": (
        ROOT / "common/scripted_effects/SCG_bicameral_effects.txt",
        ("SCG_liangyuan_zhengzhi_gengxin",),
    ),
    "unification triggers": (
        ROOT / "common/scripted_triggers/SIC_SCG_unification.txt",
        ("SIC_china_unified", "SCG_china_unified"),
    ),
    "Sichuan constitutional events": (
        ROOT / "events/SiChuan.txt",
        tuple(f"TODSIC.{event_id}" for event_id in range(1010, 1022)),
    ),
    "Ming civil-war merger decisions": (
        ROOT / "common/decisions/MNG.txt",
        (
            "MNG_SIC_hebing_yaoqing_ROC",
            "MNG_SIC_hebing_yaoqing_SRC",
            "MNG_SCG_hebing_yaoqing_ROC",
            "MNG_SCG_hebing_yaoqing_SRC",
            "MNG_SIC_taofa_ROC",
            "MNG_SIC_taofa_SRC",
            "MNG_SCG_taofa_ROC",
            "MNG_SCG_taofa_SRC",
        ),
    ),
    "Ming civil-war Sichuan merger categories": (
        ROOT / "common/decisions/categories/MNG.txt",
        ("MNG_SIC_hebing_categories", "MNG_SCG_hebing_categories"),
    ),
    "Ming civil-war Sichuan unification events": (
        ROOT / "common/decisions/MNG.txt",
        ("TODSIC.1010", "TODSIC.1012"),
    ),
    "Ming civil-war merger events": (
        ROOT / "events/mingcivwar.txt",
        tuple(f"mingcivwar.{event_id}" for event_id in range(1100, 1124)),
    ),
    "Ming merger decision localisation": (
        ROOT / "localisation/simp_chinese/TOD_Ming_l_simp_chinese.yml",
        (
            "MNG_SIC_hebing_yaoqing_ROC:",
            "MNG_SIC_hebing_yaoqing_SRC:",
            "MNG_SCG_hebing_yaoqing_ROC:",
            "MNG_SCG_hebing_yaoqing_SRC:",
            "MNG_SIC_taofa_ROC:",
            "MNG_SIC_taofa_SRC:",
            "MNG_SCG_taofa_ROC:",
            "MNG_SCG_taofa_SRC:",
        ),
    ),
    "Ming merger event localisation": (
        ROOT / "localisation/simp_chinese/TOD_MNG_civwar_l_simp_chinese.yml",
        tuple(f"mingcivwar.{event_id}.t:" for event_id in range(1100, 1124)),
    ),
    "SIC localisation": (
        ROOT / "localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml",
        (
            "SIC_qingzhengxi_sichuan:",
            "SIC_qingzhengxi_gaige_categories:",
            "SIC_daming_lixian_guo:",
            "SIC_liberal_democracy_party:0 \"帝国宪政会—清政系\"",
        ),
    ),
    "SCG localisation": (
        ROOT / "localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml",
        (
            "SCG_jianli_renmin_dahui:",
            "SCG_liangyuan_zhengzhi_categories:",
            "SCG_zhonghua_shehuizhuyi_gongheguo:",
            "SCG_council_socialism_party:0 \"同产公会（工会派）\"",
            "SCG_vanguard_socialism_party:0 \"同产公会（组织派）\"",
        ),
    ),
}

CLAUSEWITZ_FILES = (
    ROOT / "common/ai_strategy/SIC.txt",
    ROOT / "common/ai_strategy/SCG.txt",
    ROOT / "common/characters/SCG.txt",
    ROOT / "common/national_focus/chuanyudifangsi.txt",
    ROOT / "common/national_focus/sichuangemingzhengfu.txt",
    ROOT / "common/decisions/categories/SIC_constitutional_reform.txt",
    ROOT / "common/decisions/categories/SCG_bicameral_politics.txt",
    ROOT / "common/decisions/categories/SIC_wubei.txt",
    ROOT / "common/decisions/categories/SCG_postwar_economy.txt",
    ROOT / "common/decisions/categories/SCG_revolutionary_diplomacy.txt",
    ROOT / "common/decisions/categories/MNG.txt",
    ROOT / "common/decisions/SIC_constitutional_reform.txt",
    ROOT / "common/decisions/SCG_bicameral_politics.txt",
    ROOT / "common/decisions/SIC_wubei.txt",
    ROOT / "common/decisions/SCG_postwar_economy.txt",
    ROOT / "common/decisions/SCG_revolutionary_diplomacy.txt",
    ROOT / "common/dynamic_modifiers/TOD_SIC_modifiers.txt",
    ROOT / "common/dynamic_modifiers/TOD_SCG_modifiers.txt",
    ROOT / "common/ideas/SIC_idea.txt",
    ROOT / "common/ideas/SCG_idea.txt",
    ROOT / "common/ideas/SIC_SCG_companies.txt",
    ROOT / "common/military_industrial_organization/organizations/SIC_SCG_organization.txt",
    ROOT / "common/scripted_effects/SIC_chuanneijushi_scripted_effects.txt",
    ROOT / "common/scripted_effects/SCG_bicameral_effects.txt",
    ROOT / "common/scripted_triggers/SIC_SCG_unification.txt",
    ROOT / "common/scripted_triggers/ming_scripted_triggers.txt",
    ROOT / "events/SiChuan.txt",
    ROOT / "common/decisions/MNG.txt",
    ROOT / "events/mingcivwar.txt",
)

ORDERED_REQUIREMENTS = (
    (
        "SIC national spirits are country ideas rather than security-minister entries",
        ROOT / "common/ideas/SIC_idea.txt",
        "SIC_xianzheng_chenggong =",
        "TOD_foreign_minister =",
    ),
    (
        "SCG national spirits are country ideas rather than security-minister entries",
        ROOT / "common/ideas/SCG_idea.txt",
        "SCG_liangyuan_xietiao =",
        "TOD_foreign_minister =",
    ),
)

EXACT_REQUIREMENTS = (
    (
        "SCG categories remain available to the uprising tag",
        ROOT / "common/decisions/categories/SCG_bicameral_politics.txt",
        "allowed = { tag = SCG }",
    ),
    (
        "SIC unification changes the country identity",
        ROOT / "common/decisions/MNG.txt",
        "set_cosmetic_tag = SIC_daming_lixian_guo",
    ),
    (
        "SCG unification changes the country identity",
        ROOT / "common/decisions/MNG.txt",
        "set_cosmetic_tag = SCG_zhonghua_shehuizhuyi_gongheguo",
    ),
    (
        "Ming merger invitations require adjacency to the Republican Army",
        ROOT / "common/decisions/MNG.txt",
        "is_neighbor_of = ROC",
    ),
    (
        "Ming merger invitations require adjacency to the Northeast Red Army",
        ROOT / "common/decisions/MNG.txt",
        "is_neighbor_of = SRC",
    ),
    (
        "Northeast Red Army receives the 30/70 invitation weighting",
        ROOT / "events/mingcivwar.txt",
        "ai_chance = { factor = 30 }",
    ),
    (
        "Republican Army receives the 50/50 invitation weighting",
        ROOT / "events/mingcivwar.txt",
        "ai_chance = { factor = 50 }",
    ),
)

FORBIDDEN_REQUIREMENTS = (
    (
        "SIC no longer bypasses merger talks with direct ROC/SRC war decisions",
        ROOT / "common/decisions/SIC_constitutional_reform.txt",
        ("SIC_xianzheng_taofa_ROC", "SIC_xianzheng_taofa_SRC"),
    ),
    (
        "SCG no longer bypasses merger talks with direct ROC/SRC war decisions",
        ROOT / "common/decisions/SCG_bicameral_politics.txt",
        ("SCG_geming_jieguan_ROC", "SCG_geming_jieguan_SRC"),
    ),
)

ABSENT_REQUIREMENTS = (
    (
        "SIC land-rights focus was folded into the Basic Law route",
        ROOT / "common/national_focus/chuanyudifangsi.txt",
        "SIC_queren_tudi_quanyi",
    ),
    (
        "SIC land-rights decision was folded into the Basic Law route",
        ROOT / "common/decisions/SIC_constitutional_reform.txt",
        "SIC_baozhang_xiaomin_chanquan",
    ),
    (
        "SIC national event only fires from the Ming civil-war unification decision",
        ROOT / "common/national_focus/chuanyudifangsi.txt",
        "TODSIC.1010",
    ),
    (
        "SCG national event only fires from the Ming civil-war unification decision",
        ROOT / "common/national_focus/sichuangemingzhengfu.txt",
        "TODSIC.1012",
    ),
)

SIC_CONSTITUTIONAL_LAYOUT = {
    "SIC_qingzhengxi_sichuan": ((20, 6), {"SIC_tianfuzhizhi"}),
    "SIC_diaocha_xianxing": ((18, 7), {"SIC_qingzhengxi_sichuan"}),
    "SIC_gongkai_shengfu_yusuan": ((22, 7), {"SIC_qingzhengxi_sichuan"}),
    "SIC_huifu_shengzizhengju": ((18, 8), {"SIC_diaocha_xianxing"}),
    "SIC_xianzhi_jundui_canzheng": ((22, 8), {"SIC_gongkai_shengfu_yusuan"}),
    "SIC_sichuan_jibenfa": (
        (20, 9),
        {"SIC_huifu_shengzizhengju", "SIC_xianzhi_jundui_canzheng"},
    ),
    "SIC_zerenneige": ((18, 10), {"SIC_sichuan_jibenfa"}),
    "SIC_xianzheng_jiuguo_xuanyan": ((20, 10), {"SIC_sichuan_jibenfa"}),
    "SIC_junquan_guanyu_xianfa": ((22, 10), {"SIC_sichuan_jibenfa"}),
    "SIC_quanguo_zhixianpai_dahui": ((20, 11), {"SIC_xianzheng_jiuguo_xuanyan"}),
    "SIC_tongyi_bizhi_guanshui": ((18, 12), {"SIC_quanguo_zhixianpai_dahui"}),
    "SIC_sichuan_moshi": (
        (20, 12),
        {"SIC_zerenneige", "SIC_quanguo_zhixianpai_dahui", "SIC_junquan_guanyu_xianfa"},
    ),
    "SIC_guominjun_guojiahua": ((22, 12), {"SIC_quanguo_zhixianpai_dahui"}),
    "SIC_quanguo_zhixian_huiyi": (
        (20, 13),
        {"SIC_tongyi_bizhi_guanshui", "SIC_sichuan_moshi", "SIC_guominjun_guojiahua"},
    ),
    "SIC_daming_lixian_guo": ((20, 14), {"SIC_quanguo_zhixian_huiyi"}),
}

SIC_POSTWAR_REQUIREMENTS = {
    ROOT / "common/scripted_effects/SIC_chuanneijushi_scripted_effects.txt": (
        "SIC_qingzhengxi_xianzheng_gengxin",
        "SIC.qingzhengxi > 100",
        "SIC.qingzhengxi < 0",
        "SIC.xianzheng > 100",
        "SIC.xianzheng < 0",
    ),
    ROOT / "common/decisions/SIC_constitutional_reform.txt": (
        "SIC_shehui_diaocha_fa_wancheng",
        "SIC_yusuan_shenji_fa_wancheng",
        "SIC_jundui_guojiahua_fa_wancheng",
        "SIC_shengziyi_fa_wancheng",
        "SIC_neige_xinren_fa_wancheng",
        "SIC_jundui_xianfa_shiyan_wancheng",
        "SIC_gongbu_xinzheng_baipishu",
        "SIC_paichu_xianzheng_xunchaoshi",
        "SIC_qingli_difang_loushui",
        "SIC_zhaokai_laogong_ziben_xieshanghui",
        "SIC_zhaokai_quanguo_xianzheng_xuanchuan",
        "SIC_shebao_quanguo_xianzheng_tongxunshe",
        "SIC_jiedai_gepaifang_xianzheng_daibiao",
        "SIC_bianzuan_quanguo_linshifagang",
        "add_timed_idea = { idea = SIC_xianzheng_tongyi_dongyuan days = 180 }",
        "custom_effect_tooltip = SIC_shengfu_yusuan_shenji_xiaoguo",
        "custom_effect_tooltip = SIC_yu_junfang_xieshang_xiaoguo",
        "custom_effect_tooltip = SIC_qingli_difang_loushui_xiaoguo",
        "SIC_xianzheng_taofa_MNG",
        "SIC_xianzheng_taofa_MOB",
    ),
    SIC_FOCUS: (
        "has_country_flag = SIC_shehui_diaocha_fa_wancheng",
        "has_country_flag = SIC_yusuan_shenji_fa_wancheng",
        "has_country_flag = SIC_jundui_guojiahua_fa_wancheng",
        "tooltip = SIC_xianzhi_jundui_canzheng_available_tt",
        "custom_effect_tooltip = SIC_qingzhengxi_sichuan_xiaoguo",
        "custom_effect_tooltip = SIC_xianzhi_jundui_canzheng_xiaoguo",
        "custom_effect_tooltip = SIC_guominjun_guojiahua_xiaoguo",
        "country_lock_all_division_template = yes",
        "country_lock_all_division_template = no",
        "set_country_flag = SIC_daming_junxian_ready",
    ),
    SIC_LOCALISATION: (
        'SIC_daming_lixian_guo:0 "大明君宪帝国"',
        'SIC_daming_lixian_guo_DEF:0 "大明君宪帝国"',
        'SIC_daming_lixian_guo_liberal_democracy:0 "大明君宪帝国"',
        'SIC_daming_lixian_guo_liberal_democracy_DEF:0 "大明君宪帝国"',
        'SIC_daming_lixian_guo_liberal_democracy_ADJ:0 "大明"',
        'SIC_xianzhi_jundui_canzheng_available_tt:0',
        '每日政治点数获取§G+0.01§!',
        '组织度§R-1.0%§!',
        'SIC_shengfu_yusuan_shenji_xiaoguo:0',
        'SIC_yu_junfang_xieshang_xiaoguo:0',
        'SIC_qingli_difang_loushui_xiaoguo:0',
    ),
}

SCG_POSTWAR_REQUIREMENTS = {
    ROOT / "common/scripted_effects/SCG_bicameral_effects.txt": (
        "SCG.renmin_shouquan > 100",
        "SCG.renmin_shouquan < 0",
        "SCG.dangji_xietiao > 100",
        "SCG.dangji_xietiao < 0",
        "SCG.chongjian > 100",
        "SCG.chongjian < 0",
        "SCG_Sichuan_integration_effect",
    ),
    ROOT / "common/decisions/SCG_bicameral_politics.txt": (
        "SCG_liangyuan_lifa_yali",
        "days_mission_timeout = 180",
        "SCG_huifu_chengdu_gongchang_wancheng",
        "SCG_xiufu_chengyu_tielu_wancheng",
        "SCG_wending_chengshi_liangshi_wancheng",
        "SCG_anzhi_fuyuan_shibing_wancheng",
        "SCG_huifu_jiaoyu_yiliao_wancheng",
        "SCG_geming_jieguan_MNG",
        "SCG_geming_jieguan_MOB",
    ),
    SCG_FOCUS: (
        "set_variable = { SCG.renmin_shouquan = 35 }",
        "set_variable = { SCG.dangji_xietiao = 35 }",
        "check_variable = { SCG.chongjian > 79 }",
        "set_country_flag = SCG_quanguo_xianfa_ready",
    ),
}

MERGER_AND_UNIFICATION_REQUIREMENTS = {
    ROOT / "common/decisions/MNG.txt": (
        "TOD_china_unified_for_ming_civil_war = yes",
        "has_country_flag = SIC_daming_junxian_ready",
        "has_country_flag = SCG_quanguo_xianfa_ready",
        "has_country_flag = SIC_hebing_tanpan_jinxingzhong",
        "has_country_flag = SCG_hebing_tanpan_jinxingzhong",
        "set_country_flag = SIC_hebing_tanpan_jinxingzhong",
        "set_country_flag = SCG_hebing_tanpan_jinxingzhong",
        "is_subject_of = ROOT",
        "annex_country = { target = PREV transfer_troops = yes }",
    ),
    ROOT / "common/decisions/categories/MNG.txt": (
        "MNG_SIC_hebing_categories",
        "allowed = { tag = SIC }",
        "MNG_SCG_hebing_categories",
        "allowed = { tag = SCG }",
    ),
    ROOT / "common/scripted_triggers/SIC_SCG_unification.txt": (
        "TOD_china_unified_for_ming_civil_war",
        "country_exists = MNG",
        "country_exists = XIN",
        "country_exists = MOB",
    ),
    ROOT / "events/mingcivwar.txt": (
        "SIC_Sichuan_integration_effect = yes",
        "SCG_Sichuan_integration_effect = yes",
        "clr_country_flag = SIC_hebing_tanpan_jinxingzhong",
        "clr_country_flag = SCG_hebing_tanpan_jinxingzhong",
        "transfer_troops = yes",
    ),
}


def uncommented_text(path: Path) -> str:
    """Return content with line comments removed for brace counting."""
    return "\n".join(line.split("#", 1)[0] for line in path.read_text(encoding="utf-8-sig").splitlines())


def main() -> int:
    failures: list[str] = []

    if not PROTECTED_HASH_FIXTURE.exists():
        failures.append(f"missing protected-opening fixture: {PROTECTED_HASH_FIXTURE.relative_to(ROOT)}")
    else:
        expected_hashes = json.loads(PROTECTED_HASH_FIXTURE.read_text(encoding="utf-8"))
        actual_hashes = section_hashes()
        for section_name, expected_hash in expected_hashes.items():
            actual_hash = actual_hashes.get(section_name)
            if actual_hash != expected_hash:
                failures.append(
                    f"protected opening changed: {section_name} "
                    f"(expected {expected_hash}, got {actual_hash})"
                )

    validate_focus_graph("SIC", SIC_FOCUS, failures)
    validate_focus_graph("SCG", SCG_FOCUS, failures)

    sic_focuses = focus_records(SIC_FOCUS)
    for focus_id, (expected_coordinate, expected_prerequisites) in SIC_CONSTITUTIONAL_LAYOUT.items():
        record = sic_focuses.get(focus_id)
        if not record:
            failures.append(f"SIC constitutional layout: missing {focus_id}")
            continue
        actual_coordinate = (int(record["x"]), int(record["y"]))
        if actual_coordinate != expected_coordinate:
            failures.append(
                f"SIC constitutional layout: {focus_id} expected {expected_coordinate}, "
                f"got {actual_coordinate}"
            )
        actual_prerequisites = set(record["prerequisites"])
        if actual_prerequisites != expected_prerequisites:
            failures.append(
                f"SIC constitutional layout: {focus_id} expected prerequisites "
                f"{sorted(expected_prerequisites)}, got {sorted(actual_prerequisites)}"
            )
        if int(record["cost"]) != 5:
            failures.append(f"SIC constitutional route: {focus_id} is not a 35-day focus")

    for focus_id, event_id in (
        ("SIC_wendingchuanneijushi", "TODSIC.1013"),
        ("SIC_tianfuzhizhi", "TODSIC.1014"),
        ("SIC_chuanyuyili", "TODSIC.1015"),
        ("SIC_zhuluzhongyuan", "TODSIC.1016"),
        ("SIC_qingzhengxi_sichuan", "TODSIC.1017"),
        ("SIC_xianzhi_jundui_canzheng", "TODSIC.1018"),
        ("SIC_sichuan_jibenfa", "TODSIC.1019"),
        ("SIC_xianzheng_jiuguo_xuanyan", "TODSIC.1020"),
        ("SIC_sichuan_moshi", "TODSIC.1021"),
    ):
        block = str(sic_focuses.get(focus_id, {}).get("block", ""))
        if f"id = {event_id}" not in block:
            failures.append(f"SIC narrative contract: {focus_id} does not fire {event_id}")

    sichuan_events_text = (ROOT / "events/SiChuan.txt").read_text(encoding="utf-8-sig")
    for event_id in range(1013, 1017):
        block = event_block(sichuan_events_text, f"TODSIC.{event_id}")
        option_blocks = extract_blocks(block, "option")
        gameplay_effects = re.compile(
            r"\b(?:add_|set_|remove_|army_experience|navy_experience|air_experience|"
            r"country_event|create_|declare_war|load_oob|transfer_state)"
        )
        if any(gameplay_effects.search(option) for option in option_blocks):
            failures.append(
                f"SIC legacy narrative event TODSIC.{event_id} changes gameplay balance"
            )

    restriction_block = str(sic_focuses.get("SIC_xianzhi_jundui_canzheng", {}).get("block", ""))
    for required in (
        "tooltip = SIC_xianzhi_jundui_canzheng_available_tt",
        "country_lock_all_division_template = yes",
        "add_ideas = SIC_jundui_tuichu_zhengzhi",
    ):
        if required not in restriction_block:
            failures.append(f"SIC military restriction: missing {required}")

    nationalisation_block = str(sic_focuses.get("SIC_guominjun_guojiahua", {}).get("block", ""))
    for required in (
        "country_lock_all_division_template = no",
        "remove_ideas = SIC_jundui_tuichu_zhengzhi",
        "add_ideas = SIC_xianfa_guominjun",
    ):
        if required not in nationalisation_block:
            failures.append(f"SIC army nationalisation: missing {required}")

    sic_decisions_text = (ROOT / "common/decisions/SIC_constitutional_reform.txt").read_text(
        encoding="utf-8-sig"
    )
    army_negotiation_block = named_block(sic_decisions_text, "SIC_yu_junfang_xieshang")
    if "country_lock_all_division_template = no" in army_negotiation_block:
        failures.append(
            "SIC army restriction: the negotiation decision unlocks templates before nationalisation"
        )

    validate_focus_localisation(SIC_FOCUS, SIC_LOCALISATION, failures)
    validate_focus_localisation(SCG_FOCUS, SCG_LOCALISATION, failures)
    validate_custom_focus_sprites(SIC_FOCUS, failures)
    validate_custom_focus_sprites(SCG_FOCUS, failures)
    validate_postwar_ai(SIC_FOCUS, "# 清政系宪政试验", failures)
    validate_postwar_ai(SCG_FOCUS, "# 社会主义多党两院制", failures)

    sic_localisation_text = SIC_LOCALISATION.read_text(encoding="utf-8-sig")
    for event_id in range(1013, 1022):
        for suffix in ("t", "d", "a"):
            if not re.search(rf"(?m)^TODSIC\.{event_id}\.{suffix}:\d+\s+\"", sic_localisation_text):
                failures.append(f"SIC narrative localisation: missing TODSIC.{event_id}.{suffix}")
        desc_match = re.search(
            rf"(?m)^TODSIC\.{event_id}\.d:\d+\s+\"([^\"]+)\"",
            sic_localisation_text,
        )
        if desc_match and len(desc_match.group(1)) < 100:
            failures.append(f"SIC narrative localisation: TODSIC.{event_id}.d is under 100 characters")

    for focus_id in (
        "SIC_wendingchuanneijushi",
        "SIC_tianfuzhizhi",
        "SIC_chuanyuyili",
        "SIC_zhuluzhongyuan",
        *SIC_CONSTITUTIONAL_LAYOUT.keys(),
    ):
        desc_match = re.search(
            rf'(?m)^{re.escape(focus_id)}_desc:\d+\s+"([^"]+)"',
            sic_localisation_text,
        )
        if not desc_match or len(desc_match.group(1)) < 70:
            failures.append(f"SIC focus description: {focus_id}_desc is missing or under 70 characters")

    for decision_id in (
        "SIC_gongbu_xinzheng_baipishu",
        "SIC_paichu_xianzheng_xunchaoshi",
        "SIC_qingli_difang_loushui",
        "SIC_zhaokai_laogong_ziben_xieshanghui",
        "SIC_zhaokai_quanguo_xianzheng_xuanchuan",
        "SIC_shebao_quanguo_xianzheng_tongxunshe",
        "SIC_jiedai_gepaifang_xianzheng_daibiao",
        "SIC_bianzuan_quanguo_linshifagang",
    ):
        for suffix in ("", "_desc"):
            match = re.search(
                rf'(?m)^{re.escape(decision_id + suffix)}:\d+\s+"([^"]+)"',
                sic_localisation_text,
            )
            minimum = 4 if not suffix else 45
            if not match or len(match.group(1)) < minimum:
                failures.append(
                    f"SIC decision localisation: {decision_id + suffix} is missing or under {minimum} characters"
                )
    for path, required_texts in SIC_POSTWAR_REQUIREMENTS.items():
        content = path.read_text(encoding="utf-8-sig") if path.exists() else ""
        for required_text in required_texts:
            if required_text not in content:
                failures.append(f"SIC postwar contract: {path.relative_to(ROOT)} missing {required_text}")

    for path, required_texts in SCG_POSTWAR_REQUIREMENTS.items():
        content = path.read_text(encoding="utf-8-sig") if path.exists() else ""
        for required_text in required_texts:
            if required_text not in content:
                failures.append(f"SCG postwar contract: {path.relative_to(ROOT)} missing {required_text}")

    for path, required_texts in MERGER_AND_UNIFICATION_REQUIREMENTS.items():
        content = path.read_text(encoding="utf-8-sig") if path.exists() else ""
        for required_text in required_texts:
            if required_text not in content:
                failures.append(f"unification contract: {path.relative_to(ROOT)} missing {required_text}")

    merger_events = (ROOT / "events/mingcivwar.txt").read_text(encoding="utf-8-sig")
    for event_id, integration_effect in (
        ("mingcivwar.1101", "SIC_Sichuan_integration_effect = yes"),
        ("mingcivwar.1107", "SIC_Sichuan_integration_effect = yes"),
        ("mingcivwar.1113", "SCG_Sichuan_integration_effect = yes"),
        ("mingcivwar.1119", "SCG_Sichuan_integration_effect = yes"),
    ):
        block = event_block(merger_events, event_id)
        if integration_effect not in block or "transfer_troops = yes" not in block:
            failures.append(f"{event_id}: initial invitation acceptance does not fully integrate")

    for event_id, lock_flag, target_tag in (
        ("mingcivwar.1103", "SIC_hebing_tanpan_jinxingzhong", "SIC"),
        ("mingcivwar.1109", "SIC_hebing_tanpan_jinxingzhong", "SIC"),
        ("mingcivwar.1115", "SCG_hebing_tanpan_jinxingzhong", "SCG"),
        ("mingcivwar.1121", "SCG_hebing_tanpan_jinxingzhong", "SCG"),
    ):
        block = event_block(merger_events, event_id)
        required = (
            f"clr_country_flag = {lock_flag}",
            f"annex_country = {{ target = {target_tag} transfer_troops = yes }}",
        )
        if any(text not in block for text in required):
            failures.append(f"{event_id}: reverse invitation acceptance does not close cleanly")

    for event_id, lock_flag, broken_flag in (
        ("mingcivwar.1105", "SIC_hebing_tanpan_jinxingzhong", "MNG_SIC_ROC_hebing_tanpanpolie"),
        ("mingcivwar.1111", "SIC_hebing_tanpan_jinxingzhong", "MNG_SIC_SRC_hebing_tanpanpolie"),
        ("mingcivwar.1117", "SCG_hebing_tanpan_jinxingzhong", "MNG_SCG_ROC_hebing_tanpanpolie"),
        ("mingcivwar.1123", "SCG_hebing_tanpan_jinxingzhong", "MNG_SCG_SRC_hebing_tanpanpolie"),
    ):
        block = event_block(merger_events, event_id)
        required = (f"clr_country_flag = {lock_flag}", f"set_country_flag = {broken_flag}")
        if any(text not in block for text in required):
            failures.append(f"{event_id}: bilateral refusal does not unlock the war fallback")

    for event_id, accept_weight, refuse_weight in (
        ("mingcivwar.1100", 50, 50),
        ("mingcivwar.1112", 50, 50),
        ("mingcivwar.1106", 30, 70),
        ("mingcivwar.1118", 30, 70),
    ):
        block = event_block(merger_events, event_id)
        weights = [int(value) for value in re.findall(r"ai_chance\s*=\s*\{\s*factor\s*=\s*(\d+)", block)]
        if weights != [accept_weight, refuse_weight]:
            failures.append(f"{event_id}: expected AI weights {accept_weight}/{refuse_weight}, got {weights}")

    scg_characters = (ROOT / "common/characters/SCG.txt").read_text(encoding="utf-8-sig")
    advisor_tokens = re.findall(r"idea_token\s*=\s*([^\s#}]+)", scg_characters)
    duplicate_advisor_tokens = sorted(
        token for token in set(advisor_tokens) if advisor_tokens.count(token) > 1
    )
    if duplicate_advisor_tokens:
        failures.append(
            "SCG characters: duplicate advisor tokens " + ", ".join(duplicate_advisor_tokens)
        )
    for character_id in ("SCG_chen_dasan", "SCG_fu_zhong"):
        character_block = named_block(scg_characters, character_id)
        idea_token = block_value(character_block, "idea_token")
        if idea_token != character_id:
            failures.append(
                f"SCG character {character_id}: expected advisor token {character_id}, got {idea_token}"
            )

    for label, (path, required_ids) in TEXT_REQUIREMENTS.items():
        if not path.exists():
            failures.append(f"{label}: missing file {path.relative_to(ROOT)}")
            continue
        content = path.read_text(encoding="utf-8-sig")
        for content_id in required_ids:
            if content_id not in content:
                failures.append(f"{label}: missing {content_id}")

    for path in CLAUSEWITZ_FILES:
        if not path.exists():
            continue
        content = uncommented_text(path)
        balance = content.count("{") - content.count("}")
        if balance:
            failures.append(f"unbalanced braces ({balance:+d}): {path.relative_to(ROOT)}")

    for label, path, required_id, boundary_id in ORDERED_REQUIREMENTS:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8-sig")
        if content.find(required_id) > content.find(boundary_id):
            failures.append(f"{label}: {required_id} is nested too late in {path.relative_to(ROOT)}")

    for label, path, required_text in EXACT_REQUIREMENTS:
        if not path.exists() or required_text not in path.read_text(encoding="utf-8-sig"):
            failures.append(f"{label}: missing {required_text}")

    for label, path, forbidden_ids in FORBIDDEN_REQUIREMENTS:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8-sig")
        for forbidden_id in forbidden_ids:
            if forbidden_id in content:
                failures.append(f"{label}: legacy bypass {forbidden_id} remains")

    for label, path, forbidden_text in ABSENT_REQUIREMENTS:
        if path.exists() and forbidden_text in path.read_text(encoding="utf-8-sig"):
            failures.append(f"{label}: legacy event reference {forbidden_text} remains")

    if failures:
        print("Sichuan constitutional-route validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1

    print("Sichuan constitutional-route validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
