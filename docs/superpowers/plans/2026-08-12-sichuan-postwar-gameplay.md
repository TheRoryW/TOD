# Sichuan Postwar Gameplay Implementation Plan

**Status:** Implemented and statically verified on 2026-08-13. In-game campaign/UI validation remains a separate playtest step.

> **For agentic workers:** Execute inline in the current working tree. The user explicitly forbids commits, pushes, and uploads; do not use the commit steps from the generic workflow.

**Goal:** Preserve SIC's opening crisis and SCG's uprising/civil-war gameplay while rebuilding both countries' institutional, economic, military, negotiation, and national-unification gameplay after those stages.

**Architecture:** Keep the protected opening blocks byte-stable and implement later gameplay through focus agendas, decision-based laws, bounded variables, scripted update/integration effects, and a shared national-unification contract. Reuse existing art and IDs where practical so existing saves, localisation, and event references have the smallest possible migration surface.

**Tech Stack:** Hearts of Iron IV Clausewitz script, UTF-8 BOM localisation YAML, `.gfx` sprite definitions, Python static validation.

## Global Constraints

- Do not change SIC's crisis decisions, crisis GUI, SCG spawn trigger, SCG regional uprising decisions/OOBs, civil-war victory trigger, or the mutually exclusive `(25,1)` phase replacement.
- Do not commit, stage, push, or upload any file.
- Preserve ROC invitation AI weights at 50/50 and SRC invitation AI weights at 30/70.
- Merger invitations require adjacency; war is possible only after both sides reject the two-way merger.
- Every visible focus prerequisite edge introduced or moved by this plan must point from a lower `y` to a higher `y`.
- Use only existing art assets.

---

### Task 1: Strengthen the Sichuan Static Validator

**Files:**

- Modify: `tests/validate_sic_scg_constitutional_routes.py`
- Create: `tests/fixtures/sichuan_protected_opening_hashes.json`

**Interfaces:**

- Consumes the current protected SIC/SCG opening sections as the approved baseline.
- Produces checks used by all later tasks: protected hashes, focus graph validation, localisation parsing, symbol references, sprite paths, and AI reachability.

- [ ] Add a failing protected-section test that hashes SIC content before `# 清政系宪政试验`, SCG content before `# 革命成功`, `common/decisions/SIC.txt`, `common/decisions/SCG.txt`, and the SCG victory event `TODSIC.1005`.
- [ ] Run `python tests/validate_sic_scg_constitutional_routes.py` and confirm the new fixture/check fails before the fixture is populated.
- [ ] Populate the approved hashes without modifying production content.
- [ ] Add graph checks which parse focus blocks, account for SCG pre/post phase visibility, reject non-downward edges, and reject duplicate same-phase coordinates.
- [ ] Add checks for focus name/description localisation, referenced ideas, event IDs, quoted localisation lines, sprite texture existence, and non-zero AI weight on the constitutional routes.
- [ ] Run the validator and record the existing failures that Tasks 2–5 must resolve.

### Task 2: Rebuild SIC's Post-Crisis Constitutional Gameplay

**Files:**

- Modify: `common/national_focus/chuanyudifangsi.txt`
- Modify: `common/decisions/SIC_constitutional_reform.txt`
- Modify: `common/scripted_effects/SIC_chuanneijushi_scripted_effects.txt`
- Modify: `common/ideas/SIC_idea.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`
- Modify: `interface/SIC_pictures.gfx`

**Interfaces:**

- Produces bounded `SIC.qingzhengxi` and `SIC.xianzheng`, one-time reform flags, a downward-only post-crisis tree, and the `SIC_daming_junxian_ready` terminal flag.
- Keeps `SIC.gongye` and `SIC.minzhong` as inputs from the protected crisis system.

- [ ] Add failing validator expectations for all SIC reform flags, bounded-variable update effect, non-zero AI route weights, final name “大明君宪帝国”, and downward-only coordinates.
- [ ] Run the validator and confirm failures identify missing SIC post-crisis behavior.
- [ ] Add `SIC_qingzhengxi_xianzheng_gengxin` to clamp both variables and update the experiment modifier.
- [ ] Convert four reform decisions into one-time laws unlocked by their matching focuses; each consumes Qingzheng organisation, advances constitutional progress, sets a completion flag, and updates variables.
- [ ] Add provincial assembly, cabinet-confidence, and constitutional military-oath decisions for the second institutional stage.
- [ ] Rework the 16 SIC post-crisis focuses into a compact, symmetric, top-to-bottom tree; require the law flags for the Basic Law and make AI weights non-zero with crisis-aware modifiers.
- [ ] Move country identity establishment to the national-unification contract and set `SIC_daming_junxian_ready` at the terminal focus.
- [ ] Map all post-crisis focuses to existing SIC art and add only missing sprite declarations.
- [ ] Update Chinese localisation, remove duplicate keys in the touched route, and run the validator until the SIC expectations pass.

### Task 3: Rebuild SCG's Post-Revolution Bicameral Gameplay

**Files:**

- Modify: `common/national_focus/sichuangemingzhengfu.txt`
- Modify: `common/decisions/SCG_bicameral_politics.txt`
- Modify: `common/scripted_effects/SCG_bicameral_effects.txt`
- Modify: `common/dynamic_modifiers/TOD_SCG_modifiers.txt`
- Modify: `common/ideas/SCG_idea.txt`
- Modify: `events/SiChuan.txt`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`

**Interfaces:**

- Produces bounded `SCG.renmin_shouquan`, `SCG.dangji_xietiao`, and `SCG.chongjian`; recurring legislative pressure; four-of-five reconstruction; non-zero AI progression; and `SCG_quanguo_xianfa_ready`.
- Preserves every focus before `SCG_gemingchenggong` and the `(25,1)` phase switch.

- [ ] Add failing validator expectations for variable clamps, recurring pressure, one-time reconstruction decisions, four-of-five threshold, correct idea nesting, non-zero AI weights, and downward-only post-revolution coordinates.
- [ ] Run the validator and confirm the SCG failures.
- [ ] Extend `SCG_liangyuan_zhengzhi_gengxin` to clamp variables and distinguish coordination, routine politics, and crisis without unbounded stacking.
- [x] Rebalance the first meeting and bicameral focuses so at least one political decision is required before the responsibility committee and constitution.
- [ ] Add recurring legislative pressure and rebalance the four political decisions around genuine trade-offs between the two chambers.
- [ ] Make each reconstruction decision fire once, grant 20 reconstruction, add a concrete reconstruction effect, and let any four complete the reconstruction focus.
- [ ] Re-layout all post-revolution focuses with economy left, bicameral politics centre, military right, and the national route below the constitution; use availability gates instead of crossing secondary prerequisite lines where necessary.
- [ ] Give all post-revolution focuses usable AI weights and connect major economic/military outcomes to bicameral approval.
- [ ] Move SCG postwar ideas into the valid `country` idea block; replace the undefined `SCG_gonghui` event reward with a defined idea.
- [ ] Reuse existing SCG icons, correct touched localisation/effect mismatches, and run the validator until SCG expectations pass.

### Task 4: Unify Negotiated Merger and National Establishment

**Files:**

- Modify: `common/decisions/MNG.txt`
- Modify: `events/mingcivwar.txt`
- Modify: `common/scripted_effects/SCG_bicameral_effects.txt`
- Modify: `common/scripted_effects/SIC_chuanneijushi_scripted_effects.txt`
- Modify: `common/scripted_triggers/SIC_SCG_unification.txt`
- Modify: `localisation/simp_chinese/TOD_Ming_l_simp_chinese.yml`
- Modify: `localisation/simp_chinese/TOD_MNG_civwar_l_simp_chinese.yml`

**Interfaces:**

- Consumes `SIC_daming_junxian_ready` and `SCG_quanguo_xianfa_ready`.
- Produces mutually exclusive negotiation state, shared integration effects, consistent unification checks, and final cosmetic tags/events.

- [x] Add failing validator expectations for a negotiation-in-progress lock, cleanup on every terminal outcome, shared integration effects, route-ready requirements on the MNG decision, and consistent country lists.
- [ ] Run the validator and confirm the integration failures.
- [ ] Add one active-negotiation flag per Sichuan tag and prevent concurrent ROC/SRC invitations.
- [ ] Preserve adjacency, 50/50 ROC, 30/70 SRC, reverse invitation, and bilateral-refusal war behavior while clearing locks on all outcomes.
- [ ] Route successful annexations through shared SIC/SCG integration effects that also transfer unit leaders and clear negotiation state.
- [x] Make `SIC_china_unified`, `SCG_china_unified`, and `MNG_chongjiandaming_decision` check the same relevant Chinese tags.
- [x] Require the SIC/SCG ready flag before their use of the MNG national-unification decision; set final cosmetic tags and trigger national events only there.
- [ ] Complete all event/decision localisation and run the validator.

### Task 5: Sichuan Technical and Presentation Cleanup

**Files:**

- Modify: `common/characters/SCG.txt`
- Modify: `common/ai_strategy/SIC.txt`
- Modify: `common/ai_strategy/SCG.txt`
- Modify: `interface/SCG_picture.gfx`
- Modify: `interface/TOD_SCG.gfx`
- Modify: `interface/SCG_goals_shine.gfx`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`
- Modify: `tests/validate_sic_scg_constitutional_routes.py`

**Interfaces:**

- Produces a self-consistent Sichuan content package with no known missing touched localisation, sprite, advisor, or postwar AI references.

- [ ] Add failing checks for the known missing focus descriptions, malformed SCG quote, duplicate touched keys, missing sprite textures, and duplicate advisor token.
- [ ] Run the validator and confirm those failures.
- [ ] Correct the SIC/SCG localisation keys and values, SCG advisor token, and sprite definitions using existing files only.
- [ ] Replace copied inland naval production priorities with Sichuan-appropriate infantry, artillery, support, fighter, and transport priorities while retaining distinct SIC/SCG army identities.
- [ ] Run `python tests/validate_sic_scg_constitutional_routes.py`.
- [ ] Run a fresh brace/symbol scan over all modified Clausewitz files and `git diff --check`.
- [ ] Review `git diff --stat` and `git diff --name-only` to confirm only authorised files changed and that no commit, stage, push, or upload occurred.
