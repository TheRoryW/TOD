"""Static validation for the Hungary content path.

Run with: python tests/validate_hungary_content.py
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOCUS_PATH = ROOT / "common" / "national_focus" / "hungary.txt"
EVENTS_PATH = ROOT / "events" / "Hungary.txt"
GER_EVENTS_PATH = ROOT / "events" / "GER.txt"
CHARACTERS_PATH = ROOT / "common" / "characters" / "HUN.txt"
HISTORY_PATH = ROOT / "history" / "countries" / "HUN.txt"
SPRITES_PATH = ROOT / "interface" / "HUN_pictures.gfx"
LOCALISATION_PATHS = (
    ROOT / "localisation" / "english" / "TOD_Hungary_l_english.yml",
    ROOT / "localisation" / "simp_chinese" / "TOD_Hungary_l_simp_chinese.yml",
)


def uncommented(text: str) -> str:
    return re.sub(r"(?m)#.*$", "", text)


def braced_block_after(text: str, marker: str) -> str:
    marker_match = re.search(r"(?m)^[ \t]*" + re.escape(marker) + r"[ \t]*$", text)
    if not marker_match:
        raise AssertionError(f"No definition line found for {marker!r}")
    start = marker_match.start()
    definitions = list(
        re.finditer(
            r"(?m)^[ \t]*(?:focus|country_event|news_event)[ \t]*=[ \t]*\{[ \t]*$",
            text[:start],
        )
    )
    if not definitions:
        raise AssertionError(f"No enclosing definition found for {marker!r}")
    open_brace = definitions[-1].end() - 1
    depth = 0
    for index in range(open_brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise AssertionError(f"Unclosed block following {marker!r}")


def focus_block(text: str, focus_id: str) -> str:
    """Return the complete focus definition with the requested identifier."""
    return braced_block_after(text, f"id = {focus_id}")


def direct_child_blocks(text: str, label: str) -> list[str]:
    """Return balanced direct blocks beginning with ``label = {`` in ``text``."""
    blocks: list[str] = []
    for match in re.finditer(r"(?m)^\s*" + re.escape(label) + r"\s*=\s*\{", text):
        open_brace = match.end() - 1
        depth = 0
        for index in range(open_brace, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[match.start() : index + 1])
                    break
        else:
            raise AssertionError(f"Unclosed {label!r} block")
    return blocks


def top_level_character_block(text: str, character_id: str) -> str:
    """Return a character block directly contained by the characters container."""
    container = re.search(r"(?m)^\s*characters\s*=\s*\{", text)
    if not container:
        raise AssertionError("No characters container found")

    position = container.end()
    depth = 1
    while position < len(text):
        line_end = text.find("\n", position)
        if line_end == -1:
            line_end = len(text)
        line = text[position:line_end]
        match = re.match(
            r"\s*" + re.escape(character_id) + r"\s*=\s*\{", line
        )
        if depth == 1 and match:
            open_brace = position + match.end() - 1
            block_depth = 0
            for index in range(open_brace, len(text)):
                if text[index] == "{":
                    block_depth += 1
                elif text[index] == "}":
                    block_depth -= 1
                    if block_depth == 0:
                        return text[position : index + 1]
            raise AssertionError(f"Unclosed character block for {character_id}")

        depth += line.count("{") - line.count("}")
        position = line_end + 1

    raise AssertionError(f"No top-level character block found for {character_id}")


class HungaryContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.focus = uncommented(FOCUS_PATH.read_text(encoding="utf-8-sig"))
        cls.events = uncommented(EVENTS_PATH.read_text(encoding="utf-8-sig"))
        cls.germany_events = uncommented(GER_EVENTS_PATH.read_text(encoding="utf-8-sig"))
        cls.characters = uncommented(CHARACTERS_PATH.read_text(encoding="utf-8-sig"))
        cls.history = uncommented(HISTORY_PATH.read_text(encoding="utf-8-sig"))
        cls.sprites = uncommented(SPRITES_PATH.read_text(encoding="utf-8-sig"))

    def test_event_text_keys_are_localised_in_each_supported_language(self) -> None:
        required_keys = set(
            re.findall(
                r"(?m)^\s*(?:title|desc|name)\s*=\s*(TODhungary\.\d+\.[A-Za-z]+)\s*$",
                self.events,
            )
        )

        for localisation_path in LOCALISATION_PATHS:
            localisation = localisation_path.read_text(encoding="utf-8-sig")
            defined_keys = set(
                re.findall(r"(?m)^\s*(TODhungary\.\d+\.[A-Za-z]+):", localisation)
            )
            self.assertFalse(
                required_keys - defined_keys,
                f"{localisation_path.relative_to(ROOT)} is missing event text: "
                f"{', '.join(sorted(required_keys - defined_keys))}",
            )

    def test_hungary_focus_and_variant_icons_have_sprite_definitions(self) -> None:
        referenced_sprites = set(re.findall(r"\b(GFX_HUN_[A-Za-z0-9_]+)\b", self.focus))
        defined_sprites = set(
            re.findall(r'(?m)^\s*name\s*=\s*"?(GFX_HUN_[A-Za-z0-9_]+)"?', self.sprites)
        )
        self.assertFalse(
            referenced_sprites - defined_sprites,
            "Hungary content references undefined sprites: "
            f"{', '.join(sorted(referenced_sprites - defined_sprites))}",
        )

    def test_joint_aircraft_research_awards_hungary_exactly_one_bonus(self) -> None:
        focus = braced_block_after(self.focus, "id = HUN_lianhefeiji")
        event = braced_block_after(self.events, "id = TODhungary.34")

        self.assertIn("category = air_equipment", focus)
        self.assertLess(
            focus.index("add_tech_bonus"),
            focus.index("every_country"),
            "Hungary's research bonus must be granted once before allied-country events run.",
        )
        self.assertNotRegex(
            event,
            r"\bHUN\s*=\s*\{\s*add_tech_bonus",
            "Each allied recipient must not grant an additional Hungary bonus.",
        )

    def test_cabinet_restructuring_events_assign_the_selected_ministers(self) -> None:
        expected_ministers = {
            "TODhungary.13": {"HUN_Jozsef_Szell", "HUN_Kalman_Daranyi"},
            "TODhungary.14": {"HUN_Gyula_Karolyi", "HUN_Lajos_Walko"},
            "TODhungary.15": {
                "HUN_Tihamer_Fabinyi",
                "HUN_Lajos_Remenyi_Schneller",
            },
        }

        for event_id, expected in expected_ministers.items():
            event = braced_block_after(self.events, f"id = {event_id}")
            assigned = set(re.findall(r"\badd_ideas\s*=\s*(HUN_[A-Za-z0-9_]+)", event))
            self.assertEqual(
                expected,
                assigned,
                f"{event_id} must assign one of the available ministers in its slot.",
            )

    def test_focus_effect_tooltips_are_localised_in_each_supported_language(self) -> None:
        required_keys = (
            "HUN_geminzupingdeng_xiaoguo",
            "HUN_lianhefeiji_xiaoguo",
        )

        for localisation_path in LOCALISATION_PATHS:
            localisation = localisation_path.read_text(encoding="utf-8-sig")
            defined_keys = set(
                re.findall(r"(?m)^\s*([A-Za-z0-9_.]+):", localisation)
            )
            for required_key in required_keys:
                with self.subTest(
                    localisation=localisation_path.relative_to(ROOT),
                    required_key=required_key,
                ):
                    self.assertTrue(
                        required_key in defined_keys,
                        f"{localisation_path.relative_to(ROOT)} is missing focus effect text: "
                        f"{required_key}",
                    )

    def test_audited_focuses_do_not_write_dead_variables(self) -> None:
        audited_variables = {
            "HUN_geminzupingdeng": ("HUN_shaominfankang",),
            "HUN_tezhonghuazuozhan": ("HUN_lujungongji", "HUN_lujunfangyu"),
            "HUN_shandixunlian": ("HUN_shandi",),
            "HUN_qihoushiyin": ("HUN_shiying",),
            "HUN_zhaomuhaijunrenyuan": ("HUN_renyuan", "HUN_haijunrenyuan"),
            "HUN_jiaqiangrenyuanpeixun": ("HUN_peixun",),
        }

        for focus_id, variables in audited_variables.items():
            for variable in variables:
                with self.subTest(focus_id=focus_id, variable=variable):
                    self.assertNotRegex(
                        self.focus,
                        r"\badd_to_variable\s*=\s*\{\s*"
                        + re.escape(variable)
                        + r"\s*=",
                        f"{variable} must not be written anywhere in Hungary focus content "
                        f"(audited owner: {focus_id})",
                    )

    def test_new_focus_events_are_triggered_once_and_fully_localised(self) -> None:
        expected_callers = {
            "HUN.101": "HUN_fazhanduonaohejinjidai",
            "HUN.102": "HUN_geminzupingdeng",
            "HUN.103": "HUN_tezhonghuazuozhan",
            "HUN.104": "HUN_zhaomuhaijunrenyuan",
            "HUN.105": "HUN_duiwaizhengce",
        }

        self.assertRegex(
            self.events,
            r"(?m)^\s*add_namespace\s*=\s*HUN\s*$",
            "HUN.101-HUN.105 require an HUN namespace declaration",
        )

        focus_ids = re.findall(r"(?m)^\s*id\s*=\s*(HUN_[A-Za-z0-9_]+)\s*$", self.focus)
        callers_by_event = {event_id: [] for event_id in expected_callers}
        for focus_id in focus_ids:
            focus = focus_block(self.focus, focus_id)
            for event_id in expected_callers:
                if re.search(
                    r"\bcountry_event\s*=\s*\{\s*id\s*=\s*"
                    + re.escape(event_id)
                    + r"\b",
                    focus,
                ):
                    callers_by_event[event_id].append(focus_id)

        for event_id, expected_caller in expected_callers.items():
            required_keys = tuple(
                f"{event_id}.{suffix}" for suffix in ("t", "d", "a", "b")
            )
            for localisation_path in LOCALISATION_PATHS:
                localisation = localisation_path.read_text(encoding="utf-8-sig")
                defined_keys = set(
                    re.findall(r"(?m)^\s*([A-Za-z0-9_.]+):", localisation)
                )
                for required_key in required_keys:
                    with self.subTest(
                        event_id=event_id,
                        localisation=localisation_path.relative_to(ROOT),
                        required_key=required_key,
                    ):
                        self.assertTrue(
                            required_key in defined_keys,
                            f"{localisation_path.relative_to(ROOT)} is missing {event_id} text: "
                            f"{required_key}",
                        )

            event = None
            with self.subTest(event_id=event_id, contract="definition"):
                event = braced_block_after(self.events, f"id = {event_id}")
            with self.subTest(event_id=event_id, contract="caller"):
                self.assertEqual(
                    [expected_caller],
                    callers_by_event[event_id],
                    f"{event_id} must be called by exactly {expected_caller}",
                )

            if event is None:
                continue

            with self.subTest(event_id=event_id, contract="triggered only"):
                self.assertRegex(
                    event,
                    r"(?m)^\s*is_triggered_only\s*=\s*yes\s*$",
                    f"{event_id} must be triggered only by its focus",
                )
            with self.subTest(event_id=event_id, contract="no mean time to happen"):
                self.assertNotRegex(
                    event,
                    r"\bmean_time_to_happen\s*=",
                    f"{event_id} must not self-trigger over time",
                )
            with self.subTest(event_id=event_id, contract="title key"):
                self.assertRegex(
                    event,
                    r"(?m)^\s*title\s*=\s*" + re.escape(f"{event_id}.t") + r"\s*$",
                    f"{event_id} title must reference {event_id}.t",
                )
            with self.subTest(event_id=event_id, contract="description key"):
                self.assertRegex(
                    event,
                    r"(?m)^\s*desc\s*=\s*" + re.escape(f"{event_id}.d") + r"\s*$",
                    f"{event_id} description must reference {event_id}.d",
                )
            option_names = re.findall(
                r"(?m)^\s*name\s*=\s*(HUN\.\d+\.[A-Za-z]+)\s*$",
                event,
            )
            with self.subTest(event_id=event_id, contract="two option keys"):
                self.assertEqual(
                    {f"{event_id}.a", f"{event_id}.b"},
                    set(option_names),
                    f"{event_id} options must reference exactly {event_id}.a and {event_id}.b",
                )
                self.assertEqual(
                    2,
                    len(option_names),
                    f"{event_id} must define exactly two option names",
                )

    def test_diplomatic_focuses_have_concrete_effects(self) -> None:
        required_focuses = (
            "HUN_junshihezuo",
            "HUN_duiyijiaoliu",
            "HUN_duohuikeluodiya",
            "HUN_ganyuyidali",
            "HUN_xiangnankuozhang",
            "HUN_pinggufaguo",
            "HUN_wengusaierweiya",
            "HUN_jierubaergan",
            "HUN_baerganbaquan",
            "HUN_kejihezuo",
            "HUN_junshijiaoliu",
        )

        for focus_id in required_focuses:
            with self.subTest(focus_id=focus_id):
                self.assertNotRegex(
                    focus_block(self.focus, focus_id),
                    r"completion_reward\s*=\s*\{\s*\}",
                    f"{focus_id} must have a visible gameplay effect",
                )

    def test_left_nationality_route_uses_player_only_puppet_settlements(self) -> None:
        self_determination = focus_block(self.focus, "HUN_zunzhongminzuzijue")
        self.assertNotIn(
            "set_state_owner",
            self_determination,
            "Left-wing self-determination must not hand Hungarian states to an independent tag.",
        )

        expected_settlements = {
            "ROM": ("TODhungary.28", "HUN_buchangluomaniya", "HUN_release_romania_as_puppet"),
            "MOL": ("TODhungary.29", "HUN_buchangmoerduowa", "HUN_release_moldova_as_puppet"),
        }
        for tag, (event_id, integration_idea, puppet_flag) in expected_settlements.items():
            with self.subTest(tag=tag, contract="focus settlement"):
                self.assertIn(f"release_puppet = {tag}", self_determination)
                self.assertRegex(
                    self_determination,
                    r"set_autonomy\s*=\s*\{\s*target\s*=\s*"
                    + tag
                    + r"\s+autonomous_state\s*=\s*autonomy_puppet\s*\}",
                )

            event = braced_block_after(self.events, f"id = {event_id}")
            option_blocks = direct_child_blocks(event, "option")
            integration_option = next(
                option for option in option_blocks if f"add_ideas = {integration_idea}" in option
            )
            puppet_option = next(
                option for option in option_blocks if f"set_country_flag = {puppet_flag}" in option
            )
            with self.subTest(tag=tag, contract="AI integrates"):
                self.assertRegex(
                    integration_option,
                    r"ai_chance\s*=\s*\{\s*factor\s*=\s*100\s*\}",
                )
            with self.subTest(tag=tag, contract="AI never releases"):
                self.assertRegex(
                    puppet_option,
                    r"ai_chance\s*=\s*\{\s*factor\s*=\s*0\s*\}",
                )

    def test_east_wall_ai_contract_is_preserved(self) -> None:
        east_wall = focus_block(self.focus, "HUN_dongqiang")
        ai_blocks = direct_child_blocks(east_wall, "ai_will_do")
        self.assertEqual(1, len(ai_blocks), "East Wall must have one AI weighting block")
        self.assertEqual(
            "ai_will_do={base=100modifier={add=100}}",
            re.sub(r"\s+", "", ai_blocks[0]),
            "East Wall must retain its existing strong default AI tendency.",
        )

    def test_east_wall_marks_poland_as_a_persistent_member(self) -> None:
        """A transient faction relation must not let a later event remove Poland."""
        east_wall = focus_block(self.focus, "HUN_dongqiang")
        self.assertRegex(
            east_wall,
            r"POL\s*=\s*\{\s*set_country_flag\s*=\s*"
            r"TOD_EAST_WALL_POLAND_MEMBER\s*\}",
            "Poland must retain an East Wall membership marker after joining.",
        )

    def test_german_western_war_event_does_not_remove_marked_poland(self) -> None:
        """Germany's Western-war cleanup must not eject an established East Wall member."""
        western_war_news = braced_block_after(self.germany_events, "id = TODgermany.1004")
        leave_poland = western_war_news.index("POL = { leave_faction = yes }")
        safeguard = western_war_news[max(0, leave_poland - 700) : leave_poland]
        self.assertRegex(
            safeguard,
            r"NOT\s*=\s*\{\s*has_country_flag\s*=\s*"
            r"TOD_EAST_WALL_POLAND_MEMBER\s*\}",
            "The Western-war cleanup must skip Poland after it has joined East Wall.",
        )

    def test_diplomatic_focus_events_are_called_once_and_localised(self) -> None:
        expected_callers = {
            "HUN.106": "HUN_junshihezuo",
            "HUN.107": "HUN_duiyijiaoliu",
            "HUN.108": "HUN_jierubaergan",
        }
        focus_ids = re.findall(r"(?m)^\s*id\s*=\s*(HUN_[A-Za-z0-9_]+)\s*$", self.focus)

        for event_id, expected_caller in expected_callers.items():
            event = braced_block_after(self.events, f"id = {event_id}")
            callers = [
                focus_id
                for focus_id in focus_ids
                if re.search(
                    r"\bcountry_event\s*=\s*\{\s*id\s*=\s*"
                    + re.escape(event_id)
                    + r"\b",
                    focus_block(self.focus, focus_id),
                )
            ]
            self.assertEqual([expected_caller], callers)
            self.assertRegex(event, r"(?m)^\s*is_triggered_only\s*=\s*yes\s*$")

            for localisation_path in LOCALISATION_PATHS:
                localisation = localisation_path.read_text(encoding="utf-8-sig")
                for suffix in ("t", "d", "a", "b"):
                    self.assertRegex(
                        localisation,
                        r"(?m)^\s*" + re.escape(f"{event_id}.{suffix}") + r":",
                        f"{localisation_path.relative_to(ROOT)} is missing {event_id}.{suffix}",
                    )

    def test_active_hungary_roster_has_no_czech_copied_content(self) -> None:
        copied_character_ids = {
            "HUN_vojtyech_luzha",
            "HUN_josef_shnejdarek",
            "HUN_richard_tesarzhik",
            "HUN_sergej_vojcechovsky",
            "HUN_rudolf_viest",
            "HUN_alois_vicherek",
            "HUN_antonin_hasal",
            "HUN_jaroslav_fajfr",
            "HUN_jan_golian",
            "HUN_karel_janousek",
            "HUN_josef_frantisek",
            "HUN_ludvik_krejci",
            "HUN_karel_vaclav_petrik",
            "HUN_karel_kuttelwascher",
            "HUN_ludvik_svoboda",
            "HUN_frantisek_havel",
            "HUN_stefan_osusky",
            "HUN_ferdinand_catlos",
            "HUN_jozef_tiso",
            "HUN_vojtech_tuka",
            "HUN_konrad_henlein",
            "HUN_gustav_husak",
        }
        recruited = set(
            re.findall(r"(?m)^\s*recruit_character\s*=\s*(HUN_[A-Za-z0-9_]+)\s*$", self.history)
        )
        defined = {
            character_id
            for character_id in copied_character_ids
            if re.search(
                r"(?m)^\s*" + re.escape(character_id) + r"\s*=\s*\{",
                self.characters,
            )
        }

        self.assertFalse(
            copied_character_ids & recruited,
            "Hungary history still recruits copied characters: "
            + ", ".join(sorted(copied_character_ids & recruited)),
        )
        self.assertFalse(
            defined,
            "Hungary character definitions still include copied characters: "
            + ", ".join(sorted(defined)),
        )
        self.assertNotRegex(self.history, r"\bHUN_CZE_[A-Za-z0-9_]+\b")
        self.assertNotRegex(self.characters, r"\bHUN_CZE_[A-Za-z0-9_]+\b")
        copied_sprite = re.compile(
            r"\b(?:GFX_Portrait_czechoslovakia_[A-Za-z0-9_]*|GFX_idea_CZE_[A-Za-z0-9_]*)\b",
            re.IGNORECASE,
        )
        self.assertNotRegex(self.history, copied_sprite)
        self.assertNotRegex(self.characters, copied_sprite)

    def test_native_officers_have_required_alternate_command_roles(self) -> None:
        required_roles = {
            "HUN_ferenc_szombathelyi": ("corps_commander", "hill_fighter", 3),
            "HUN_hugo_sonyi": ("corps_commander", "engineer", 2),
            "HUN_dezso_laszlo": ("corps_commander", "organizer", 1),
            "HUN_henrik_werth": ("field_marshal", None, 3),
        }

        for character_id, (role, trait, skill) in required_roles.items():
            with self.subTest(character_id=character_id):
                character = top_level_character_block(self.characters, character_id)
                role_match = re.search(
                    r"\b" + role + r"\s*=\s*\{(?P<block>.*?)^\s*\}",
                    character,
                    re.MULTILINE | re.DOTALL,
                )
                self.assertIsNotNone(
                    role_match,
                    f"{character_id} must have a {role} command role",
                )
                assert role_match is not None
                role_block = role_match.group("block")
                self.assertRegex(
                    role_block,
                    r"\bskill\s*=\s*" + str(skill) + r"\b",
                    f"{character_id} must have command skill {skill}",
                )
                if trait is not None:
                    self.assertRegex(
                        role_block,
                        r"\btraits\s*=\s*\{[^}]*\b" + re.escape(trait) + r"\b",
                        f"{character_id} must have the {trait} trait",
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
