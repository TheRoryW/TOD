from pathlib import Path
import re
import sys


ROOT = Path(__file__).parents[1]
TARGETS = [
    ROOT / "history" / "countries" / "UKR - wukelan.txt",
    ROOT / "history" / "countries" / "LAF - Lanfang.txt",
]

errors = []
for path in TARGETS:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if re.match(r'\s*if\s*=\s*\{', line)
            and 'has_dlc = "Man the Guns"' in ''.join(lines[index:index + 3])
        ),
        None,
    )
    if start is None:
        errors.append(f"{path.name}: missing Man the Guns fallback block")
        continue

    depth = 0
    nested_else = False
    for line in lines[start:]:
        if re.match(r'\s*else\s*=\s*\{', line):
            nested_else = depth == 1
            break
        depth += line.count('{') - line.count('}')
        if depth == 0:
            break
    if not nested_else:
        errors.append(f"{path.name}: Man the Guns fallback else is not nested inside its if block")

compatibility_ideas = (ROOT / "common/ideas/TOD_missing_vanilla_ideas.txt").read_text(encoding="utf-8-sig")
if "IRQ_anglo_iraqi_mutual_defense_agreement" not in compatibility_ideas:
    errors.append("missing Iraqi mutual-defense idea still queried by the current British MIO")

fra_air_bba = (ROOT / "history/units/FRA_1936_air_bba.txt").read_text(encoding="utf-8-sig")
fra_air_legacy = (ROOT / "history/units/FRA_1936_air_legacy.txt").read_text(encoding="utf-8-sig")
fra_navy = (ROOT / "history/units/FRA_1936.txt").read_text(encoding="utf-8-sig")
for path, air_oob in (("FRA_1936_air_bba.txt", fra_air_bba), ("FRA_1936_air_legacy.txt", fra_air_legacy)):
    if '"Béarn" = {' in air_oob:
        errors.append(f"{path}: carrier aircraft still target removed carrier Béarn")
    if '"Atlantique CV 01" = {' not in air_oob:
        errors.append(f"{path}: carrier aircraft must target the active French carrier")
if 'name = "Atlantique CV 01"' not in fra_navy:
    errors.append("FRA_1936.txt: active carrier for the French air OOB is missing")

blt_history = (ROOT / "history/countries/BLT.txt").read_text(encoding="utf-8-sig")
naval_oob_index = blt_history.find('set_naval_oob = "BLT_naval_mtg"')
hull_tech_index = blt_history.find("basic_ship_hull_light")
if hull_tech_index < 0:
    errors.append("BLT.txt: missing destroyer hull technology for the Baltic fleet")
elif naval_oob_index < 0 or naval_oob_index < hull_tech_index:
    errors.append("BLT.txt: Baltic naval OOB loads before its required hull technology")

bra_history = (ROOT / "history/countries/BRA - baxi.txt").read_text(encoding="utf-8-sig")
if "autonomous_state = kr_default_puppet" in bra_history:
    errors.append("BRA - baxi.txt: Uruguay still uses the unavailable kr_default_puppet autonomy level")
if "autonomous_state = autonomy_puppet" not in bra_history:
    errors.append("BRA - baxi.txt: Uruguay must use the loaded generic puppet autonomy level")

ideologies = (ROOT / "common/ideologies/00_ideologies.txt").read_text(encoding="utf-8-sig")
for ideology in ("democratic", "fascism", "communism", "neutrality"):
    if not re.search(rf"(?m)^\t{ideology}\s*=\s*\{{", ideologies):
        errors.append(f"00_ideologies.txt: hidden compatibility ideology {ideology} is disabled")
    if not re.search(rf"(?m)^\t\t\t{ideology}_subtype\s*=\s*\{{\}}", ideologies):
        errors.append(f"00_ideologies.txt: hidden compatibility ideology {ideology} has no subtype")

legacy_portraits = {
    "history/countries/GRE - Greece.txt": "gfx/leaders/GRE/Portrait_GRE_Elisfrios_Venizelos.png",
    "history/countries/HDF - Haiti-Dominica Federation.txt": "gfx/leaders/HDF/Portrait_HDF_Rafael_Trujillo.png",
    "history/countries/INA - yishubeifei.txt": "gfx/leaders/INA/Portrait_INA_Italo_Gariboldi.tga",
    "history/countries/KHM - Khmer.txt": "gfx/leaders/KHM/Portrait_KHM_Sim_Var.png",
    "history/countries/LAB.txt": "gfx/leaders/LAB/Portrait_LAB_Juozas_Tūbelis.png",
    "history/countries/LAM - Lubeck and Mecklenburg.txt": "gfx/leaders/LAM/Portrait_LAM_Paul_Behnvke.png",
    "history/countries/LPC - Luzon.txt": "gfx/leaders/LPC/Portrait_LPC_Zheng_Yongqing.png",
    "history/countries/MES.txt": "gfx/leaders/MES/Portrait_MES_Nicolás_Carrasco.png",
    "history/countries/NOR.txt": "gfx/leaders/DEN/Portrait_DEN_Thorvald_Stauning.png",
    "history/countries/SAX - saxon.txt": "gfx/leaders/SAX/Portrait_SAX_Friedrich_Christian.png",
}
for relative_path, portrait_path in legacy_portraits.items():
    history = (ROOT / relative_path).read_text(encoding="utf-8-sig")
    if f'picture = "{portrait_path}"' not in history:
        errors.append(f"{relative_path}: legacy country-leader portrait does not use its existing explicit path")

khm_history = (ROOT / "history/countries/KHM - Khmer.txt").read_text(encoding="utf-8-sig")
for portrait_path in (
    "gfx/leaders/SIA/Portrait_SIA_Jin_Yuting.png",
    "gfx/leaders/SIA/Portrait_SIA_Chen_Jiaxiang.png",
    "gfx/leaders/SIA/Portrait_SIA_Wu_Bie.png",
    "gfx/leaders/MEX/Portrait_MEX_Lazaro_Cardenas.dds",
):
    history = khm_history if "/SIA/" in portrait_path else (ROOT / "history/countries/MES.txt").read_text(encoding="utf-8-sig")
    if f'picture = "{portrait_path}"' not in history:
        errors.append(f"legacy country-leader portrait {portrait_path} does not use its existing explicit path")

if errors:
    print("FAIL")
    print("\n".join(errors))
    sys.exit(1)

print("PASS: Ukrainian and Lanfang naval-tech fallbacks are valid nested if/else blocks")
