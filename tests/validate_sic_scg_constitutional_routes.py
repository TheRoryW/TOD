"""Static contract checks for the Sichuan constitutional-route content.

This intentionally stays small: it checks the content identifiers that make the
two routes playable and catches unbalanced Clausewitz blocks before launching
the game.
"""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

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
        ("SIC_kaizhan_shehui_diaocha", "SIC_zhichi_quanguo_zhixianpai"),
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
        ("SIC_xianzheng_chenggong", "SIC_daming_lixian_guo"),
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
        ("TODSIC.1010", "TODSIC.1011", "TODSIC.1012"),
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
    ROOT / "common/national_focus/chuanyudifangsi.txt",
    ROOT / "common/national_focus/sichuangemingzhengfu.txt",
    ROOT / "common/decisions/categories/SIC_constitutional_reform.txt",
    ROOT / "common/decisions/categories/SCG_bicameral_politics.txt",
    ROOT / "common/decisions/SIC_constitutional_reform.txt",
    ROOT / "common/decisions/SCG_bicameral_politics.txt",
    ROOT / "common/dynamic_modifiers/TOD_SIC_modifiers.txt",
    ROOT / "common/dynamic_modifiers/TOD_SCG_modifiers.txt",
    ROOT / "common/ideas/SIC_idea.txt",
    ROOT / "common/ideas/SCG_idea.txt",
    ROOT / "common/scripted_effects/SCG_bicameral_effects.txt",
    ROOT / "common/scripted_triggers/SIC_SCG_unification.txt",
    ROOT / "events/SiChuan.txt",
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
        ROOT / "common/national_focus/chuanyudifangsi.txt",
        "set_cosmetic_tag = SIC_daming_lixian_guo",
    ),
    (
        "SCG unification changes the country identity",
        ROOT / "common/national_focus/sichuangemingzhengfu.txt",
        "set_cosmetic_tag = SCG_zhonghua_shehuizhuyi_gongheguo",
    ),
)


def uncommented_text(path: Path) -> str:
    """Return content with line comments removed for brace counting."""
    return "\n".join(line.split("#", 1)[0] for line in path.read_text(encoding="utf-8-sig").splitlines())


def main() -> int:
    failures: list[str] = []

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

    if failures:
        print("Sichuan constitutional-route validation failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1

    print("Sichuan constitutional-route validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
