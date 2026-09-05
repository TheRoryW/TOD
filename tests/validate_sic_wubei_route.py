"""Static contract for SIC's mirrored Wubei political route."""

from __future__ import annotations

import re
import sys

sys.path.insert(0, str(__file__.replace("validate_sic_wubei_route.py", "")))

from validate_sic_scg_constitutional_routes import ROOT, focus_records, localisation_keys, named_block


WUBEI_FOCUSES = {
    "SIC_wubei_xinan_judian": (30, 6, ("SIC_chuanyuyili",)),
    "SIC_zhengdun_xinan_jungong": (28, 7, ("SIC_wubei_xinan_judian",)),
    "SIC_qingdian_chuanjun_mensheng": (32, 7, ("SIC_wubei_xinan_judian",)),
    "SIC_jiena_shuntian_liuwangzhe": (28, 8, ("SIC_zhengdun_xinan_jungong", "SIC_qingdian_chuanjun_mensheng")),
    "SIC_nanbei_wubei_heliu": (32, 8, ("SIC_zhengdun_xinan_jungong", "SIC_qingdian_chuanjun_mensheng")),
    "SIC_chongjian_xinan_wubei_zonghui": (30, 9, ("SIC_jiena_shuntian_liuwangzhe", "SIC_nanbei_wubei_heliu")),
    "SIC_junguan_zhuanren_zhengwu": (28, 10, ("SIC_chongjian_xinan_wubei_zonghui",)),
    "SIC_shiye_jianjun_gangling": (30, 10, ("SIC_chongjian_xinan_wubei_zonghui",)),
    "SIC_tongyi_chuanjun_renshi": (32, 10, ("SIC_chongjian_xinan_wubei_zonghui",)),
    "SIC_sichuan_junzheng_huiyi": (30, 11, ("SIC_junguan_zhuanren_zhengwu", "SIC_shiye_jianjun_gangling", "SIC_tongyi_chuanjun_renshi")),
    "SIC_tongyi_junxu_biaozhun": (28, 12, ("SIC_sichuan_junzheng_huiyi",)),
    "SIC_shengying_qiye_junxuhua": (30, 12, ("SIC_sichuan_junzheng_huiyi",)),
    "SIC_junzheng_jiguan_yitihua": (32, 12, ("SIC_sichuan_junzheng_huiyi",)),
    "SIC_quanguo_wubei_daibiao_huiyi": (30, 13, ("SIC_tongyi_junxu_biaozhun", "SIC_shengying_qiye_junxuhua", "SIC_junzheng_jiguan_yitihua")),
    "SIC_wubei_tongguo": (30, 14, ("SIC_quanguo_wubei_daibiao_huiyi",)),
}

WUBEI_DECISIONS = {
    "SIC_anzhi_liuwang_junguan", "SIC_jieshou_jungong_dangan", "SIC_shencha_beilai_mingce",
    "SIC_tiaohe_chuanjun_baoding", "SIC_sheli_xinan_wubei_xuetang", "SIC_qingli_liuwang_zhengzhi_zhaiwu",
    "SIC_paiqian_junguan_jiaoliutuan", "SIC_tongyi_buqiang_huopao_biaozhun", "SIC_huafen_nanbei_junxu_dingdan",
    "SIC_jianli_lianhe_junshi_yanjiushi", "SIC_xietiao_zhongyuan_zuozhan", "SIC_chuli_nanbei_lingdaoquan",
}


def main() -> int:
    failures: list[str] = []
    focus_path = ROOT / "common/national_focus/chuanyudifangsi.txt"
    focus_text = focus_path.read_text(encoding="utf-8-sig")
    records = focus_records(focus_path)
    for focus_id, (x, y, prerequisites) in WUBEI_FOCUSES.items():
        record = records.get(focus_id)
        if record is None:
            failures.append(f"missing focus: {focus_id}")
            continue
        if (record["x"], record["y"], record["cost"]) != (x, y, 5):
            failures.append(f"{focus_id}: expected ({x}, {y}, 5), got ({record['x']}, {record['y']}, {record['cost']})")
        for prerequisite in prerequisites:
            if prerequisite not in record["prerequisites"]:
                failures.append(f"{focus_id}: missing prerequisite {prerequisite}")

    reunion_block = records.get("SIC_chongjian_xinan_wubei_zonghui", {}).get("block", "")
    reunion_groups = re.findall(r"prerequisite\s*=\s*\{([^}]*)\}", str(reunion_block), re.S)
    if not any("SIC_jiena_shuntian_liuwangzhe" in group and "SIC_nanbei_wubei_heliu" in group for group in reunion_groups):
        failures.append("Wubei reunion must use one OR prerequisite block for both branch choices")

    for focus_id in ("SIC_jiena_shuntian_liuwangzhe", "SIC_nanbei_wubei_heliu"):
        if "custom_trigger_tooltip" not in str(records.get(focus_id, {}).get("block", "")):
            failures.append(f"{focus_id}: missing localized branch availability tooltip")
    final_block = str(records.get("SIC_wubei_tongguo", {}).get("block", ""))
    if "set_country_flag = SIC_daming_junzheng_ready" not in final_block or "set_cosmetic_tag" in final_block:
        failures.append("SIC_wubei_tongguo must set readiness only, without changing the cosmetic tag")

    qingzheng_block = str(records.get("SIC_qingzhengxi_sichuan", {}).get("block", ""))
    wubei_root_block = str(records.get("SIC_wubei_xinan_judian", {}).get("block", ""))
    if "focus = SIC_wubei_xinan_judian" not in qingzheng_block:
        failures.append("Qingzheng root must remain mutually exclusive with the Wubei root")
    if "mutually_exclusive" in wubei_root_block and "focus = SIC_qingzhengxi_sichuan" in wubei_root_block:
        failures.append("Wubei root must not duplicate Qingzheng's mutual-exclusion declaration")

    sic_decisions = ROOT / "common/decisions/SIC_wubei.txt"
    category = ROOT / "common/decisions/categories/SIC_wubei.txt"
    effects = ROOT / "common/scripted_effects/SIC_chuanneijushi_scripted_effects.txt"
    modifiers = ROOT / "common/dynamic_modifiers/TOD_SIC_modifiers.txt"
    ideas = ROOT / "common/ideas/SIC_idea.txt"
    events = ROOT / "events/SiChuan.txt"
    stg_events = ROOT / "events/STG.txt"
    unification = ROOT / "common/decisions/MNG.txt"
    mio = ROOT / "common/military_industrial_organization/organizations/SIC_SCG_organization.txt"
    for path in (sic_decisions, category, effects, modifiers, ideas, events, stg_events, unification, mio):
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        if path == sic_decisions:
            for decision in WUBEI_DECISIONS:
                if decision not in text:
                    failures.append(f"missing Wubei decision: {decision}")
        elif path == effects:
            for required in ("SIC_wubei_integration_gengxin", "SIC_wubei_integration_bianhua"):
                if required not in text:
                    failures.append(f"missing Wubei scripted effect: {required}")
        elif path == modifiers and "SIC_wubei_zonghui" not in text:
            failures.append("missing Wubei dynamic modifier")
        elif path == ideas:
            for required in ("SIC_chuanjun_baoding_chongtu", "SIC_xinan_wubei_xuetang", "SIC_nanbei_lingdaoquan_zhengyi", "SIC_daming_junzheng_guo_idea"):
                if required not in text:
                    failures.append(f"missing Wubei idea: {required}")
            leadership_dispute = named_block(text, "SIC_nanbei_lingdaoquan_zhengyi")
            if "improve_relations_maintain_cost_factor = 0.25" not in leadership_dispute:
                failures.append("SIC north-south leadership dispute must raise improve-relations upkeep by 25%")
            if "improve_relation_modifier" in leadership_dispute:
                failures.append("SIC north-south leadership dispute uses an undefined modifier")
        elif path == events:
            for event_id in range(1030, 1044):
                if f"TODSIC.{event_id}" not in text:
                    failures.append(f"missing Wubei event TODSIC.{event_id}")
        elif path == stg_events:
            for flag in ("TOD_STG_wubei_in_exile", "TOD_STG_wubei_in_power"):
                if flag not in text:
                    failures.append(f"missing persistent Shuntian outcome flag: {flag}")
        elif path == unification:
            for required in ("SIC_daming_junzheng_ready", "SIC_daming_junzheng_guo", "TODSIC.1039", "TODSIC.1040"):
                if required not in text:
                    failures.append(f"missing Wubei unification integration: {required}")
        elif path == mio:
            for token in ("TOD_sichuan_mio_trait_wubei_rifle_standard", "TOD_sichuan_mio_trait_wubei_artillery_standard", "TOD_sichuan_mio_trait_wubei_ammunition_order", "TOD_sichuan_mio_trait_wubei_machinegun_order", "TOD_sichuan_mio_trait_wubei_signal_standard"):
                if token not in text:
                    failures.append(f"missing Wubei MIO trait: {token}")

    localisation_path = ROOT / "localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml"
    keys, duplicates, malformed_quotes = localisation_keys(localisation_path)
    ignored_duplicates = {
        "SIC_scout_plane_equipment_0",
        "SIC_scout_plane_equipment_0_short",
        "SIC_scout_plane_equipment_1_short",
    }
    for identifier in (*WUBEI_FOCUSES, *WUBEI_DECISIONS):
        for key in (identifier, f"{identifier}_desc"):
            if key not in keys:
                failures.append(f"{localisation_path.name}: missing {key}")
    for key in ("SIC_wubei_exile_available_tt", "SIC_wubei_collaboration_available_tt", "SIC_wubei_integration_80_tt", "SIC_daming_junzheng_guo", "SIC_daming_junzheng_guo_idea"):
        if key not in keys:
            failures.append(f"{localisation_path.name}: missing {key}")
    failures.extend(
        f"{localisation_path.name}: duplicate {item}"
        for item in duplicates
        if item.split(" at line", 1)[0] not in ignored_duplicates
    )
    failures.extend(f"{localisation_path.name}: malformed quote {item}" for item in malformed_quotes)

    if failures:
        print("SIC Wubei validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("SIC Wubei validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
