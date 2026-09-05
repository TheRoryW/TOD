"""Static contract for SCG's post-revolution economic and political redesign."""

from __future__ import annotations

import hashlib
import json
import re
import sys

sys.path.insert(0, str(__file__.replace("validate_scg_postrevolution_redesign.py", "")))

from validate_sic_scg_constitutional_routes import ROOT, focus_records, localisation_keys, named_block


ECONOMIC_FOCUSES = {
    "SCG_sichuan_jingji_chongjian_weiyuanhui": (15, 2), "SCG_zuzhigonghui": (13, 3), "SCG_zuzhi_nonghui": (17, 3),
    "SCG_qiyegaizu": (12, 4), "SCG_gongrenzhichang": (14, 4), "SCG_wendingliangshigongji": (16, 4), "SCG_zuzhidangyuanxiaxiang": (18, 4),
    "SCG_wanquanguoyouhua": (12, 5), "SCG_gongsiheying": (14, 5), "SCG_tudigaige": (16, 5), "SCG_jitihuanongye": (18, 5),
    "SCG_shixingjihuajingji": (12, 6), "SCG_jiandaochalilun": (14, 6), "SCG_shehuizhuyigaizao": (16, 6), "SCG_xinjingjizhengce": (18, 6),
    "SCG_chanyelianzhenghe": (12, 7), "SCG_gongyefanbunongye": (14, 7), "SCG_nongyegongrengaizao": (16, 7), "SCG_hunhejingjitizhi": (18, 7),
    "SCG_sichuan_gongyehua_gangyao": (15, 8), "SCG_chengyu_gongye_zoulang": (13, 9), "SCG_chuannan_ziyuan_zhenghe": (17, 9), "SCG_tianfu_gongyehua": (15, 10),
}

POLITICAL_FOCUSES = {
    "SCG_geminghou_diyici_huiyi": (25, 2), "SCG_lianhezhengfu": (25, 3), "SCG_duodang_shehuizhuyi": (25, 4),
    "SCG_jianli_renmin_dahui": (24, 5), "SCG_jianli_zhengdanghui": (26, 5), "SCG_liangyuan_yishi_guize": (25, 6),
    "SCG_zeren_renminweiyuanhui": (25, 7), "SCG_sichuan_shehuizhuyi_xianfa": (25, 8), "SCG_renmin_zhangwo_sichuan": (23, 9),
    "SCG_chengli_geming_waijiao_lianluochu": (27, 9), "SCG_changshe_quanguo_daibiaochu": (23, 10), "SCG_quanguo_shehuizhuyi_zhengdang_huiyi": (27, 10),
    "SCG_quanguo_gongnong_lianluo": (24, 11), "SCG_quanguo_tongzhan_lianhehui": (26, 11), "SCG_quanguo_gongtong_gangling": (25, 12),
    "SCG_quanguo_renminjun": (25, 13), "SCG_zhonghua_zhixian_dabiao_dahui": (25, 14), "SCG_zhonghua_shehuizhuyi_gongheguo": (25, 15),
}

MILITARY_COORDINATES = {
    "SCG_renminjundui": (35, 2), "SCG_guanbingpingdeng": (33, 3), "SCG_chongzugemingjundui": (35, 3), "SCG_jianlizhengwei": (37, 3),
    "SCG_jianliminbingzhidu": (32, 4), "SCG_junduizhuanyehua": (38, 4), "SCG_minbingweifu": (31, 5), "SCG_minbingweizhu": (33, 5),
    "SCG_yiliangqusheng": (37, 5), "SCG_yizhiqusheng": (39, 5), "SCG_youqiubiying": (30, 6), "SCG_ziligengsheng": (32, 6),
    "SCG_zhuangbeixiafang": (34, 6), "SCG_kuodazhuangbeishengchan": (36, 6), "SCG_huoliyanfa": (38, 6), "SCG_tishengzhuangbeishuiping": (40, 6),
    "SCG_shenruqunzhong": (31, 7), "SCG_zizaowuqi": (33, 7), "SCG_tishengchanpingongyi": (37, 7), "SCG_quanfuwuzhuang": (39, 7),
}

POSTWAR_DECISIONS = {
    "SCG_zhiding_shengchan_zhibiao", "SCG_jizhong_zhongdian_gongye_lian", "SCG_tiaozheng_liangshi_shougoujia", "SCG_butie_nongye_jixie",
    "SCG_kuoda_hezuoshe", "SCG_jianli_gongren_jishu_weiyuanhui", "SCG_fafang_shengchan_xukezheng", "SCG_jianguan_siren_ziben",
    "SCG_zhengqu_zhengzhi_chengren", "SCG_yuanzhu_shehuizhuyi_youdang", "SCG_paiqian_gongnong_daibiaotuan", "SCG_jianli_geming_lianluochu",
    "SCG_geming_jieguan_GOS", "SCG_geming_jieguan_GPS", "SCG_geming_jieguan_MNG", "SCG_geming_jieguan_MOB",
    "SCG_geming_jieguan_STG", "SCG_geming_jieguan_XBJ", "SCG_geming_jieguan_XIN",
}

NARRATIVE_EVENTS = {
    "SCG_zhangwochengdujushi": 1065,
    "SCG_hezuo": 1066,
    "SCG_jianlihongjun": 1067,
    "SCG_gemingchenggong": 1068,
    "SCG_qiyegaizu": 1069,
    "SCG_wanquanguoyouhua": 1070,
    "SCG_gongsiheying": 1071,
    "SCG_tudigaige": 1072,
    "SCG_jitihuanongye": 1073,
    "SCG_chanyelianzhenghe": 1074,
    "SCG_gongyefanbunongye": 1075,
    "SCG_nongyegongrengaizao": 1076,
    "SCG_hunhejingjitizhi": 1077,
    "SCG_renminjundui": 1078,
    "SCG_jianlizhengwei": 1079,
    "SCG_jianliminbingzhidu": 1080,
    "SCG_geminghou_diyici_huiyi": 1081,
    "SCG_duodang_shehuizhuyi": 1082,
    "SCG_liangyuan_yishi_guize": 1083,
    "SCG_zeren_renminweiyuanhui": 1084,
}


def normalised_military_block(block: str) -> str:
    block = re.sub(r"(?m)^\s*[xy]\s*=\s*\d+\s*$", "", block)
    block = re.sub(r"\s*prerequisite\s*=\s*\{\s*focus\s*=\s*SCG_gemingchenggong\s*\}", "", block)
    block = re.sub(r"\s*country_event\s*=\s*\{\s*id\s*=\s*TODSIC\.10(?:6[5-9]|7[0-9]|80)\s*days\s*=\s*1\s*\}", "", block)
    return re.sub(r"\n{3,}", "\n\n", block).strip()


def main() -> int:
    failures: list[str] = []
    focus_path = ROOT / "common/national_focus/sichuangemingzhengfu.txt"
    records = focus_records(focus_path)
    for focus_id, (x, y) in {**ECONOMIC_FOCUSES, **POLITICAL_FOCUSES, **MILITARY_COORDINATES}.items():
        record = records.get(focus_id)
        if record is None:
            failures.append(f"missing focus: {focus_id}")
        elif (record["x"], record["y"]) != (x, y):
            failures.append(f"{focus_id}: expected ({x}, {y}), got ({record['x']}, {record['y']})")

    fixture_path = ROOT / "tests/fixtures/scg_military_focus_contract.json"
    for focus_id, expected_hash in json.loads(fixture_path.read_text(encoding="utf-8")).items():
        block = str(records.get(focus_id, {}).get("block", ""))
        actual_hash = hashlib.sha256(normalised_military_block(block).encode("utf-8")).hexdigest()
        if actual_hash != expected_hash:
            failures.append(f"{focus_id}: military content changed outside allowed layout/root connection edits")

    focus_text = focus_path.read_text(encoding="utf-8-sig")
    for required in (
        "set_variable = { SCG.geming_shengwang = 20 }", "SCG_sichuan_gongyehua_gangyao", "SCG_quanguo_gongtong_gangling",
        "check_variable = { SCG.chongjian > 69 }", "check_variable = { SCG.renmin_shouquan > 59 }", "check_variable = { SCG.dangji_xietiao > 59 }",
    ):
        if required not in focus_text:
            failures.append(f"missing post-revolution focus contract: {required}")

    if "continuous_focus_position = { x = 100 y = 1000 }" not in focus_text:
        failures.append("SCG continuous focuses are not parked in the left-side empty area")

    expected_prerequisites = {
        "SCG_duodang_shehuizhuyi": {"SCG_lianhezhengfu"},
        "SCG_quanguo_tongzhan_lianhehui": {"SCG_quanguo_shehuizhuyi_zhengdang_huiyi"},
    }
    for focus_id, expected in expected_prerequisites.items():
        actual = set(records.get(focus_id, {}).get("prerequisites", []))
        if actual != expected:
            failures.append(f"{focus_id}: expected prerequisites {sorted(expected)}, got {sorted(actual)}")

    commissar_block = str(records.get("SCG_jianlizhengwei", {}).get("block", ""))
    for forbidden in (
        "SCG_liangyuan_yishi_guize",
        "SCG.renmin_shouquan",
        "SCG.dangji_xietiao",
    ):
        if forbidden in commissar_block:
            failures.append(f"SCG_jianlizhengwei: obsolete bicameral requirement remains: {forbidden}")

    for focus_id, event_id in NARRATIVE_EVENTS.items():
        focus_block = str(records.get(focus_id, {}).get("block", ""))
        if f"id = TODSIC.{event_id}" not in focus_block:
            failures.append(f"{focus_id}: does not fire immersion event TODSIC.{event_id}")

    bicameral_path = ROOT / "common/scripted_effects/SCG_bicameral_effects.txt"
    bicameral_block = named_block(bicameral_path.read_text(encoding="utf-8-sig"), "SCG_liangyuan_zhengzhi_gengxin")
    for required in ("hidden_effect = {", "remove_ideas = SCG_liangyuan_zhengzhi_zhengchang", "remove_ideas = SCG_liangyuan_zhengzhi_weiji"):
        if required not in bicameral_block:
            failures.append(f"SCG bicameral maintenance is not hidden correctly: {required}")

    for path, identifiers in {
        ROOT / "common/decisions/SCG_postwar_economy.txt": ("SCG_zhiding_shengchan_zhibiao", "SCG_butie_nongye_jixie", "SCG_fafang_shengchan_xukezheng"),
        ROOT / "common/decisions/SCG_revolutionary_diplomacy.txt": ("SCG_zhengqu_zhengzhi_chengren", "SCG_jianli_geming_lianluochu"),
        ROOT / "events/SiChuan.txt": tuple(f"TODSIC.{event_id}" for event_id in range(1050, 1085)),
        ROOT / "common/scripted_effects/SCG_bicameral_effects.txt": ("SCG_geming_shengwang_gengxin",),
    }.items():
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        for identifier in identifiers:
            if identifier not in text:
                failures.append(f"{path.name}: missing {identifier}")

    localisation_path = ROOT / "localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml"
    keys, duplicates, malformed_quotes = localisation_keys(localisation_path)
    for identifier in (*ECONOMIC_FOCUSES, *POLITICAL_FOCUSES):
        for key in (identifier, f"{identifier}_desc"):
            if key not in keys:
                failures.append(f"{localisation_path.name}: missing {key}")
    for identifier in POSTWAR_DECISIONS:
        for key in (identifier, f"{identifier}_desc"):
            if key not in keys:
                failures.append(f"{localisation_path.name}: missing {key}")
    for event_id in range(1050, 1085):
        for key in (f"TODSIC.{event_id}.t", f"TODSIC.{event_id}.d", f"TODSIC.{event_id}.a"):
            if key not in keys:
                failures.append(f"{localisation_path.name}: missing {key}")
    for key in ("TODSIC.1060.b", "TODSIC.1060.c", "SCG_postwar_economy_categories", "SCG_postwar_economy_categories_desc", "SCG_geming_waijiao_categories", "SCG_geming_waijiao_categories_desc"):
        if key not in keys:
            failures.append(f"{localisation_path.name}: missing {key}")

    for source_path in (
        ROOT / "common/ideas/SCG_idea.txt",
        ROOT / "common/dynamic_modifiers/TOD_SCG_modifiers.txt",
    ):
        source_text = source_path.read_text(encoding="utf-8-sig")
        if source_path.name == "SCG_idea.txt":
            diplomacy_network = named_block(source_text, "SCG_geming_waijiao_lianluowang")
            if "improve_relations_maintain_cost_factor = -0.10" not in diplomacy_network:
                failures.append("SCG revolutionary diplomacy network must reduce improve-relations upkeep by 10%")
            if "improve_relation_modifier" in diplomacy_network:
                failures.append("SCG revolutionary diplomacy network uses an undefined modifier")
        idea_ids = re.findall(r"(?m)^\s*(SCG_[A-Za-z0-9_]+)\s*=\s*\{", source_text)
        for idea_id in idea_ids:
            for key in (idea_id, f"{idea_id}_desc"):
                if key not in keys:
                    failures.append(f"{localisation_path.name}: missing SCG spirit/modifier localisation {key}")
    failures.extend(f"{localisation_path.name}: duplicate {item}" for item in duplicates)
    failures.extend(f"{localisation_path.name}: malformed quote {item}" for item in malformed_quotes)

    if failures:
        print("SCG post-revolution validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("SCG post-revolution validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
