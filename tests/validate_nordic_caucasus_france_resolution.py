from pathlib import Path
import re
import sys


ROOT = Path(__file__).parents[1]


def event_block(source: str, event_id: str) -> str:
    match = re.search(rf"id\s*=\s*{re.escape(event_id)}", source)
    if not match:
        raise AssertionError(f"missing event {event_id}")
    start = source.rfind("country_event = {", 0, match.start())
    if start < 0:
        raise AssertionError(f"{event_id} is not a country event")
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise AssertionError(f"{event_id} has unbalanced braces")


def require(text: str, pattern: str, message: str) -> None:
    if not re.search(pattern, text, flags=re.DOTALL):
        raise AssertionError(message)


try:
    fin_ideas = (ROOT / "common" / "ideas" / "Finland_ideas.txt").read_text(encoding="utf-8-sig")
    swe_ideas = (ROOT / "common" / "ideas" / "sweden_ideas.txt").read_text(encoding="utf-8-sig")
    ai_plans = (ROOT / "common" / "ai_strategy" / "default.txt").read_text(encoding="utf-8-sig")
    caucasus = (ROOT / "events" / "Caucasus.txt").read_text(encoding="utf-8-sig")
    russia = (ROOT / "events" / "Russia.txt").read_text(encoding="utf-8-sig")
    france = (ROOT / "events" / "FRA.txt").read_text(encoding="utf-8-sig")
    peace_ai = (ROOT / "common" / "peace_conference" / "ai_peace" / "00_misc.txt").read_text(encoding="utf-8-sig")
    syr_chinese = (ROOT / "localisation" / "simp_chinese" / "TOD_SYR_l_simp_chinese.yml").read_text(encoding="utf-8-sig")
    syr_english = (ROOT / "localisation" / "english" / "TOD_SYR_l_english.yml").read_text(encoding="utf-8-sig")
    blr_characters_path = ROOT / "common" / "characters" / "BLR.txt"
    blr_history = (ROOT / "history" / "countries" / "BLR - Belarus-Lithuania Federation.txt").read_text(encoding="utf-8-sig")
    ita_characters = (ROOT / "common" / "characters" / "ITA.txt").read_text(encoding="utf-8-sig")
    ita_history = (ROOT / "history" / "countries" / "ITA - yidali.txt").read_text(encoding="utf-8-sig")
    descriptor = (ROOT / "descriptor.mod").read_text(encoding="utf-8-sig")
    ita_bop_path = ROOT / "common" / "bop" / "ITA_bop.txt"

    for ideas, idea, enemy in (
        (fin_ideas, "FIN_nordic_unification_offensive", "SWE"),
        (swe_ideas, "SWE_nordic_unification_offensive", "FIN"),
    ):
        require(ideas, rf"{idea}\s*=\s*\{{.*?attrition\s*=\s*-0\.4", f"{idea} lacks attrition reduction")
        require(ideas, rf"{idea}\s*=\s*\{{.*?supply_consumption_factor\s*=\s*-0\.4", f"{idea} lacks supply reduction")
        require(ideas, rf"{idea}\s*=\s*\{{.*?tag\s*=\s*{enemy}.*?attack_bonus_against\s*=\s*2\.0", f"{idea} lost target attack bonus")

    for tag, enemy in (("FIN", "SWE"), ("SWE", "FIN")):
        require(ai_plans, rf"TOD_{tag}_nordic_unification_offensive_ai\s*=\s*\{{.*?has_idea\s*=\s*{tag}_nordic_unification_offensive.*?has_war_with\s*=\s*{enemy}.*?type\s*=\s*front_control.*?tag\s*=\s*{enemy}.*?execution_type\s*=\s*rush.*?execute_order\s*=\s*yes", f"{tag} lacks an active Nordic offensive AI plan")

    caucasus_win = event_block(caucasus, "TODCaucasus.2")
    require(caucasus_win, r"OR\s*=\s*\{\s*tag\s*=\s*ARM\s*tag\s*=\s*GEO\s*tag\s*=\s*AZR", "Caucasus victory is not available to all three front members")
    require(caucasus_win, r"218\s*=\s*\{\s*is_controlled_by\s*=\s*ROOT\s*\}", "Caucasus capital capture does not use the winning country")
    require(caucasus_win, r"surrender_progress\s*>\s*0\.5", "Caucasus victory lacks the 50% surrender fallback")
    require(caucasus_win, r"ARM\s*=\s*\{\s*add_to_faction\s*=\s*CAU\s*\}", "Armenia does not invite transformed Caucasus into the Revolutionary Front")
    caucasus_formation = event_block(caucasus, "TODCaucasus.0")
    for tag in ("GEO", "AZR"):
        require(caucasus_formation, rf"{tag}\s*=\s*\{{.*?is_in_faction\s*=\s*yes.*?leave_faction\s*=\s*yes", f"{tag} does not leave its previous faction")
        require(caucasus_formation, rf"add_to_faction\s*=\s*{tag}", f"Armenia does not invite {tag} into the Revolutionary Front")

    nordic_settlement = event_block(russia, "TODRussia.13")
    require(nordic_settlement, r"has_country_flag\s*=\s*\{\s*flag\s*=\s*TOD_RUS_winter_war_started\s+days\s*>\s*365", "Nordic settlement is not delayed by one year")
    require(nordic_settlement, r"111\s*=\s*\{\s*is_controlled_by\s*=\s*RUS\s*\}", "Russian victory does not require Helsinki")
    require(nordic_settlement, r"146\s*=\s*\{\s*set_state_owner_to\s*=\s*RUS.*?set_state_controller_to\s*=\s*RUS", "Russian victory does not cede Finnish Karelia")
    require(nordic_settlement, r"195\s*=\s*\{\s*controller\s*=\s*\{\s*OR\s*=\s*\{\s*tag\s*=\s*FIN\s*tag\s*=\s*SWE\s*tag\s*=\s*NOR", "Nordic victory does not require Saint Petersburg")
    require(nordic_settlement, r"transfer_state\s*=\s*213.*?transfer_state\s*=\s*216", "Nordic victory does not cede the full Kola Peninsula")
    require(nordic_settlement, r"white_peace\s*=\s*FIN.*?white_peace\s*=\s*SWE.*?white_peace\s*=\s*NOR", "Nordic settlement does not white-peace all Nordic belligerents")

    french_settlement = event_block(france, "TODfrance.16")
    for tag in ("RIN", "BAV", "AUS"):
        require(french_settlement, rf"release\s*=\s*{tag}.*?set_autonomy\s*=\s*\{{\s*target\s*=\s*{tag}\s+autonomous_state\s*=\s*autonomy_puppet", f"French settlement does not release and puppet {tag}")
    require(french_settlement, r"news_event\s*=\s*\{\s*id\s*=\s*TODfrance\.17", "French settlement does not announce the peace")
    for target in ("GER", "ENG"):
        require(peace_ai, rf"TOD_FRA_puppet_{target}\s*=\s*\{{.*?peace_action_type\s*=\s*puppet.*?ROOT\s*=\s*\{{\s*tag\s*=\s*FRA\s*\}}.*?tag\s*=\s*{target}.*?ai_desire\s*=\s*2000", f"France has no high-priority puppet tendency for {target}")

    require(syr_chinese, r"(?m)^SYR:0\s+\"法属黎凡特\"$", "Syria's Chinese country name is not French Levant")
    require(syr_english, r"(?m)^SYR:0\s+\"French Levant\"$", "Syria's English country name is not French Levant")

    if not blr_characters_path.exists():
        raise AssertionError("Belarus has no character definition for its provisional committee")
    blr_characters = blr_characters_path.read_text(encoding="utf-8-sig")
    require(blr_characters, r"BLR_Provisional_Committee\s*=\s*\{.*?country_leader\s*=\s*\{.*?ideology\s*=\s*conservative_democracy_subtype", "Belarus's provisional committee lacks a conservative-democratic country-leader role")
    require(blr_characters, r"large\s*=\s*\"gfx/leaders/Europe/Portrait_Europe_Generic_1\.dds\"", "Belarus's provisional committee lacks its safe temporary portrait")
    require(blr_history, r"(?m)^recruit_character\s*=\s*BLR_Provisional_Committee$", "Belarus does not recruit its provisional committee at game start")

    require(ita_characters, r"ITA_Vittorio_Emanuele_III\s*=\s*\{.*?large\s*=\s*\"gfx/leaders/ITA/Portrait_ITA_Vittorio_Emanuele_III_1\.png\"", "Italy's consociational leader has no portrait definition")
    require(ita_history, r"(?m)^recruit_character\s*=\s*ITA_Vittorio_Emanuele_III$", "Italy does not recruit its starting leader, so the Italian puppet can lack a portrait")
    require(descriptor, r'(?m)^replace_path="common/bop"$', "The descriptor does not isolate vanilla BOP files that require excluded vanilla characters")
    if not ita_bop_path.exists():
        raise AssertionError("The MOD's intended Italian BOP file is missing")

except AssertionError as exc:
    print(f"FAIL: {exc}")
    sys.exit(1)

print("PASS: Nordic, Caucasus, and French settlement chains are wired")
