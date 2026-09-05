# SIC Wubei Route Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a complete SIC Wubei political route with mirrored focus layout, persistent Shuntian outcome detection, Wubei integration decisions, two narrative outcomes, and the shared national name “大明军政国”.

**Architecture:** The route is appended to the existing SIC post-crisis focus section and uses a single clamped `SIC.wubei_integration` variable plus one dynamic modifier. Shuntian’s conference event records global outcome flags so SIC can distinguish an in-power Wubei clique from exiles even after state changes. Both branches converge mechanically and set one readiness flag; the existing Ming civil-war national unification decision remains the only place that applies the cosmetic tag.

**Tech Stack:** Hearts of Iron IV national focuses, decisions, events, scripted effects, dynamic modifiers, ideas, MIO special traits, AI strategy, Simplified Chinese localization, Python static validation.

**Spec:** `docs/superpowers/specs/2026-08-24-sichuan-enterprises-wubei-scg-redesign-design.md`

## Global Constraints

- Attach the route to `SIC_chuanyuyili`; center it on X=30 and mirror the Qingzheng center X=20 around X=25.
- Every new focus costs 5 (35 days), every prerequisite line points downward, and same-row X gaps are at least 2.
- The two branch choices are mutually exclusive but reconverge at `SIC_chongjian_xinan_wubei_zonghui`.
- The reconvergence focus uses one `prerequisite = { ... }` block containing both branch IDs, so either mutually exclusive choice is sufficient; it must not use two separate prerequisite blocks.
- Both outcomes use the same cosmetic tag and displayed national name: 大明军政国.
- `MNG_chongjiandaming_decision` remains the only cosmetic-tag transition.
- Do not alter SIC’s pre-crisis or crisis content and do not modify `common/decisions/SIC.txt`.
- Reuse existing focus, idea, decision, and MIO artwork; do not create image files.
- Preserve unrelated worktree changes; do not stage, commit, push, or upload Git changes.

---

### Task 1: Add the Wubei route contract validator

**Files:**
- Create: `tests/validate_sic_wubei_route.py`

**Interfaces:**
- Consumes: parsing helpers from `tests/validate_sic_scg_constitutional_routes.py`.
- Produces: a standalone static contract for coordinates, cost, prerequisites, state flags, decisions, events, readiness flag, cosmetic tag, and localization.

- [ ] **Step 1: Write the failing validator**

Create a validator with the following immutable focus map:

```python
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
```

For `SIC_chongjian_xinan_wubei_zonghui`, the two listed prerequisite IDs form one OR group in a single Clausewitz prerequisite block. The three prerequisites of `SIC_sichuan_junzheng_huiyi` remain separate AND requirements.

Use `focus_records()` to assert each focus exists, has the mapped X/Y, has `cost = 5`, and contains every mapped prerequisite. Also assert:

```python
assert "mutually_exclusive = { focus = SIC_nanbei_wubei_heliu }" in records["SIC_jiena_shuntian_liuwangzhe"]["block"]
assert "mutually_exclusive = { focus = SIC_jiena_shuntian_liuwangzhe }" in records["SIC_nanbei_wubei_heliu"]["block"]
assert "set_country_flag = SIC_daming_junzheng_ready" in records["SIC_wubei_tongguo"]["block"]
assert "set_cosmetic_tag" not in records["SIC_wubei_tongguo"]["block"]
```

Read the related files and assert these exact IDs or strings exist:

```python
REQUIRED_DECISIONS = (
    "SIC_anzhi_liuwang_junguan", "SIC_jieshou_jungong_dangan",
    "SIC_shencha_beilai_mingce", "SIC_tiaohe_chuanjun_baoding",
    "SIC_sheli_xinan_wubei_xuetang", "SIC_qingli_liuwang_zhengzhi_zhaiwu",
    "SIC_paiqian_junguan_jiaoliutuan", "SIC_tongyi_buqiang_huopao_biaozhun",
    "SIC_huafen_nanbei_junxu_dingdan", "SIC_jianli_lianhe_junshi_yanjiushi",
    "SIC_xietiao_zhongyuan_zuozhan", "SIC_chuli_nanbei_lingdaoquan",
)
REQUIRED_EVENTS = tuple(f"TODSIC.{event_id}" for event_id in range(1030, 1044))
```

The validator must additionally assert:

- `TOD_STG_wubei_in_power` and `TOD_STG_wubei_in_exile` occur in `events/STG.txt`;
- `SIC_wubei_integration_update` exists in `SIC_chuanneijushi_scripted_effects.txt`;
- `SIC_wubei_zonghui` exists in `TOD_SIC_modifiers.txt`;
- `SIC_daming_junzheng_guo` is used by the SIC branch of `MNG_chongjiandaming_decision`;
- localization contains `SIC_daming_junzheng_guo:0 "大明军政国"`, `_DEF`, `_ADJ`, and every focus/decision/event key.

- [ ] **Step 2: Run the validator and confirm it fails before implementation**

Run:

```powershell
python tests/validate_sic_wubei_route.py
```

Expected: exit code 1 listing missing Wubei focuses and support content.

---

### Task 2: Persist the Shuntian Wubei outcome

**Files:**
- Modify: `events/STG.txt`
- Modify: `tests/validate_sic_wubei_route.py`

**Interfaces:**
- Consumes: existing event `TOD_STG.11` and its three result options.
- Produces: mutually exclusive global flags `TOD_STG_wubei_in_power` and `TOD_STG_wubei_in_exile`.

- [ ] **Step 1: Update the three conference result options**

In `TOD_STG.11.a`, before completing `STG_wubeijueqi`, add:

```hoi4
clr_global_flag = TOD_STG_wubei_in_exile
set_global_flag = TOD_STG_wubei_in_power
```

In both `TOD_STG.11.b` and `TOD_STG.11.c`, before completing their focus, add:

```hoi4
clr_global_flag = TOD_STG_wubei_in_power
set_global_flag = TOD_STG_wubei_in_exile
```

- [ ] **Step 2: Run the state-flag portion of the validator**

Run `python tests/validate_sic_wubei_route.py`.

Expected: Shuntian flag assertions pass; route assertions still fail.

---

### Task 3: Implement Wubei integration state and national spirits

**Files:**
- Modify: `common/scripted_effects/SIC_chuanneijushi_scripted_effects.txt`
- Modify: `common/dynamic_modifiers/TOD_SIC_modifiers.txt`
- Modify: `common/ideas/SIC_idea.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`

**Interfaces:**
- Consumes: country variable `SIC.wubei_integration`.
- Produces: `SIC_wubei_integration_update`, dynamic modifier `SIC_wubei_zonghui`, two branch-conflict spirits, two resolved spirits, and final national spirit `SIC_daming_junzheng_guo_idea`.

- [ ] **Step 1: Add the clamping and stage updater**

Create `SIC_wubei_integration_update` that clamps the variable to 0—100 and writes these dynamic-modifier backing variables:

| Integration | stability | PP gain | army org | planning | factory output | mobilization | MIO funds |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0—29 | −10% | −10% | −5% | 0 | 0 | 0 | 0 |
| 30—69 | 0 | 0 | 0 | 0 | 0 | 0 | +10% |
| 70—79 | 0 | 0 | +5% | +5% | +10% | 0 | +10% |
| 80—100 | 0 | 0 | +5% | +5% | +10% | +15% | +15% |

Use variable names beginning `SIC_wubei_zonghui_` and set all seven on every branch so old values cannot leak between stages.

- [ ] **Step 2: Add the dynamic modifier**

Add `SIC_wubei_zonghui` with these modifier keys:

```hoi4
stability_factor = SIC_wubei_zonghui_wending
political_power_gain = SIC_wubei_zonghui_zhengzhi
army_org_factor = SIC_wubei_zonghui_zuzhi
planning_speed = SIC_wubei_zonghui_jihua
industrial_capacity_factory = SIC_wubei_zonghui_chanchu
mobilization_speed = SIC_wubei_zonghui_dongyuan
military_industrial_organization_funds_gain = SIC_wubei_zonghui_jungongzijin
```

- [ ] **Step 3: Add branch and final ideas**

Add these country ideas using existing SIC military/industry pictures:

| Idea | Effects |
|---|---|
| `SIC_chuanjun_baoding_chongtu` | stability −8%, PP gain −10%, army advisor cost +15% |
| `SIC_xinan_wubei_xuetang` | army experience gain +15%, army advisor cost −25%, land doctrine cost −5% |
| `SIC_nanbei_lingdaoquan_zhengyi` | PP gain −10%, improve relations −25%, production efficiency growth −5% |
| `SIC_nanbei_junxu_xieding` | factory output +8%, production efficiency growth +10%, land-equipment research +5% |
| `SIC_nanbei_junxu_tixi_bengkui` | factory output −15%, production efficiency growth −20%, army org −10% |
| `SIC_daming_junzheng_guo_idea` | stability +8%, PP gain +10%, factory output +10%, war support +10% |

The war-collapse spirit is maintained by hidden event `TODSIC.1043`, first scheduled 30 days after choosing collaboration and then rescheduled every 30 days while the collaboration path remains active. It replaces `SIC_nanbei_junxu_xieding` while SIC is at war with STG and restores that agreement when the war ends.

- [ ] **Step 4: Add visible variable and idea localization**

Add names and descriptions for all ideas plus scripted localization lines for `SIC.wubei_integration`. Descriptions must explain the 30/70/80 thresholds and not expose raw variable keys.

- [ ] **Step 5: Run the Wubei validator**

Expected: modifier/effect assertions pass; focus, decision, and event assertions still fail.

---

### Task 4: Add the mirrored Wubei focus route

**Files:**
- Modify: `common/national_focus/chuanyudifangsi.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`

**Interfaces:**
- Consumes: `SIC_chuanyuyili`, Shuntian global flags, integration updater, Wubei ideas, and shared enterprise IDs.
- Produces: the 15 focus IDs in `WUBEI_FOCUSES` and readiness flag `SIC_daming_junzheng_ready`.

- [ ] **Step 1: Add the root and mutual exclusions**

Append the route after the existing constitutional route. `SIC_wubei_xinan_judian` must:

- require `SIC_chuanyuyili`;
- be mutually exclusive with `SIC_qingzhengxi_sichuan`, `SIC_yonglizhengtong`, and `SIC_zanshibaochizhongli`;
- initialize integration to 15;
- add `SIC_wubei_zonghui` and call `SIC_wubei_integration_update`;
- trigger `TODSIC.1030` one day later.

Add the reciprocal `SIC_wubei_xinan_judian` mutual exclusion to `SIC_qingzhengxi_sichuan` without changing any other Qingzheng effect.

- [ ] **Step 2: Add the two pre-branch focuses and choices**

Both Y=7 focuses add integration +5. The exile choice is available when:

```hoi4
OR = {
    has_global_flag = TOD_STG_wubei_in_exile
    NOT = { country_exists = STG }
}
```

The collaboration choice is available when:

```hoi4
country_exists = STG
has_global_flag = TOD_STG_wubei_in_power
```

Wrap both conditions in `custom_trigger_tooltip` and localize unresolved, exile, and in-power explanations. The exile choice sets `SIC_wubei_exile_path`, adds `SIC_chuanjun_baoding_chongtu`, and triggers `TODSIC.1031`. The collaboration choice sets `SIC_wubei_collaboration_path`, adds `SIC_nanbei_lingdaoquan_zhengyi`, triggers `TODSIC.1032`, and schedules hidden checker `TODSIC.1043` after 30 days. Each adds integration +5 and calls the updater.

- [ ] **Step 3: Add the common route and exact integration rewards**

Use the approved coordinates. Apply these integration changes:

- `SIC_chongjian_xinan_wubei_zonghui`: +5 and unlock category tooltip;
- each Y=10 focus: +5;
- `SIC_sichuan_junzheng_huiyi`: +5 and trigger `TODSIC.1036`;
- each Y=12 focus: +5;
- `SIC_quanguo_wubei_daibiao_huiyi`: no automatic integration; require `SIC.wubei_integration > 79` with localized tooltip and trigger `TODSIC.1038`;
- `SIC_wubei_tongguo`: set `SIC_daming_junzheng_ready`, add 100 PP and 5% stability, but do not change cosmetic tag.

At the end of every focus that changes integration, call `SIC_wubei_integration_update = yes`.

- [ ] **Step 4: Add concrete non-variable rewards**

Use this focus-to-reward mapping:

| Focus | Additional reward |
|---|---|
| 整顿西南军工 | 1×100% industry bonus, 25 army XP |
| 清点川军门生 | 50 PP, 30 army XP |
| 军官转任政务 | 100 PP, stability −3% |
| 实业建军纲领 | one military factory in controlled 831, MIO funds gain timed idea for 180 days |
| 统一川军人事 | army XP 35, command power 25 |
| 统一军需标准 | add the Wubei special traits described in Task 5 |
| 省营企业军需化 | one military factory in controlled 830 or 831, civilian construction speed −5% for 180 days |
| 军政机关一体化 | war support +10%, mobilization speed timed bonus for 180 days |

- [ ] **Step 5: Add focus localization and icons**

Add names, 100—180 Chinese-character descriptions, available-condition tooltips, and completion tooltips for all 15 focuses. Reuse existing SIC/STG/MNG sprites; run the existing sprite validator to reject an undefined token.

- [ ] **Step 6: Run layout validation**

Run:

```powershell
python tests/validate_sic_wubei_route.py
python tests/validate_sic_scg_constitutional_routes.py
```

Expected: all focus, coordinate, cost, and downward-edge checks pass; decisions/events may still fail.

---

### Task 5: Add Wubei decisions and MIO route traits

**Files:**
- Create: `common/decisions/categories/SIC_wubei.txt`
- Create: `common/decisions/SIC_wubei.txt`
- Modify: `common/military_industrial_organization/organizations/SIC_SCG_organization.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`
- Modify: `localisation/simp_chinese/TOD_SIC_SCG_companies_l_simp_chinese.yml`

**Interfaces:**
- Consumes: branch flags, `SIC.wubei_integration`, shared MIO IDs, and the integration updater.
- Produces: category `SIC_wubei_zhenghe_categories`, twelve one-time branch decisions, and five Wubei-only MIO special traits.

- [ ] **Step 1: Create the category and all twelve decisions**

The category is allowed for SIC, visible after `SIC_chongjian_xinan_wubei_zonghui`, and uses the existing political-address icon. Implement the exact decision costs and integration gains from the spec. Every decision must:

- be visible only for its branch flag;
- be `fire_only_once = yes`;
- require enough PP and, where specified, command power;
- add the specified integration amount in `remove_effect`;
- call `SIC_wubei_integration_update = yes`;
- have a localized `_desc` explaining the political tradeoff.

The two final conflict-resolution decisions replace the negative branch spirit with its positive resolved spirit.

- [ ] **Step 2: Add Wubei special traits to the five shared MIOs**

Add one `position = { x = 10 y = 0 }` special trait to each organization. All are available from `SIC_tongyi_junxu_biaozhun` and use unique tokens:

| Organization | Trait token | Effects |
|---|---|---|
| 成都兵工厂 | `TOD_sichuan_mio_trait_wubei_rifle_standard` | build cost −5%, reliability +5% |
| 重庆武器修理所 | `TOD_sichuan_mio_trait_wubei_artillery_standard` | reliability +10%, resource need −5% |
| 川康子弹厂 | `TOD_sichuan_mio_trait_wubei_ammunition_order` | efficiency gain +10%, cap +5% |
| 华兴机器厂 | `TOD_sichuan_mio_trait_wubei_machinegun_order` | soft attack +5%, build cost −3% |
| 电信机械修造厂 | `TOD_sichuan_mio_trait_wubei_signal_standard` | MIO research bonus +10%, reliability +5% |

- [ ] **Step 3: Run decision and enterprise validation**

Run:

```powershell
python tests/validate_sic_wubei_route.py
python tests/validate_sichuan_enterprises.py
```

Expected: decision and shared-enterprise contracts pass.

---

### Task 6: Add Wubei narrative events

**Files:**
- Modify: `events/SiChuan.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`

**Interfaces:**
- Consumes: focus and branch flags.
- Produces: `TODSIC.1030`—`TODSIC.1042`.

- [ ] **Step 1: Add the country events**

Use this fixed event allocation:

| ID | Title | Trigger source |
|---:|---|---|
| 1030 | 成都军官俱乐部的陌生来客 | route root |
| 1031 | 北来的列车 | exile choice |
| 1032 | 顺天发来的密电 | collaboration choice |
| 1033 | 行李箱中的军工图纸 | receive-archives decision |
| 1034 | 川军与保定门生 | integration reaches 30 on exile path |
| 1035 | 厂长、师长与省府 | 实业建军纲领 |
| 1036 | 四川军政会议开幕 | 四川军政会议 |
| 1037 | 同一种步枪 | 统一军需标准 |
| 1038 | 全国武备代表齐聚成都 | 全国武备代表会议 |
| 1039 | 大明军政国：西南武备政府 | national unification, exile path |
| 1040 | 大明军政国：南北军政共治 | national unification, collaboration path |
| 1041 | 大明军政国宣告成立 | exile news event |
| 1042 | 南北武备系共建军政国家 | collaboration news event |
| 1043 | hidden 30-day STG war-state checker | collaboration choice and self-reschedule |

Every event must be `is_triggered_only = yes`. Event 1031 schedules 1034 after seven days. The military-archive decision triggers 1033; “实业建军纲领” triggers 1035; “统一军需标准” triggers 1037. Events 1039 and 1040 respectively fire news events 1041 and 1042 and have distinct descriptions while naming the country identically. Event 1043 is hidden and has no narrative localization.

- [ ] **Step 2: Add complete event localization**

Each event gets `.t`, `.d`, and at least one option key. Descriptions target 130—220 Chinese characters and distinguish the two paths through personnel, institutions, and relations with Shuntian rather than through the country name.

- [ ] **Step 3: Run event validation**

Run `python tests/validate_sic_wubei_route.py`.

Expected: all event IDs and localization keys pass.

---

### Task 7: Route the existing national unification decision to 大明军政国

**Files:**
- Modify: `common/decisions/MNG.txt`
- Modify: `common/ideas/SIC_idea.txt`
- Modify: `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`
- Modify: `common/ai_strategy/SIC.txt`

**Interfaces:**
- Consumes: `SIC_daming_junzheng_ready`, branch flags, final idea, and events 1039/1040.
- Produces: cosmetic tag `SIC_daming_junzheng_guo` and AI completion of both branches.

- [ ] **Step 1: Expand the SIC readiness condition**

Change the SIC portion of `MNG_chongjiandaming_decision.available` to accept either readiness flag:

```hoi4
OR = {
    NOT = { tag = SIC }
    has_country_flag = SIC_daming_junxian_ready
    has_country_flag = SIC_daming_junzheng_ready
}
```

- [ ] **Step 2: Add the Wubei SIC completion branch before the constitutional SIC branch**

Use an `if` limited by `tag = SIC` and `SIC_daming_junzheng_ready`. It must:

```hoi4
set_cosmetic_tag = SIC_daming_junzheng_guo
add_ideas = SIC_daming_junzheng_guo_idea
```

Then dispatch `TODSIC.1039` when `SIC_wubei_exile_path` is set and `TODSIC.1040` when `SIC_wubei_collaboration_path` is set. Convert the existing constitutional SIC block to `else_if` so only one SIC identity executes.

- [ ] **Step 3: Add cosmetic-tag localization**

Add:

```yaml
 SIC_daming_junzheng_guo:0 "大明军政国"
 SIC_daming_junzheng_guo_DEF:0 "大明军政国"
 SIC_daming_junzheng_guo_ADJ:0 "大明"
```

Add ideology-specific name/DEF/ADJ keys for the ruling ideology reached by the route and a description that branches with scripted localization according to the exile/collaboration flag.

- [ ] **Step 4: Add AI strategy gates**

Give SIC one weighted plan for the exile branch when STG is absent or `TOD_STG_wubei_in_exile` is set, and one for collaboration when STG exists with `TOD_STG_wubei_in_power`. The AI must not select a locked branch or receive zero weight on common Wubei focuses.

- [ ] **Step 5: Run the full static suite**

Run:

```powershell
python tests/validate_sic_wubei_route.py
python tests/validate_sichuan_enterprises.py
python tests/validate_sic_scg_constitutional_routes.py
```

Expected: all exit 0; the existing constitutional “大明君宪帝国” branch still passes its identity checks.

---

### Task 8: In-game verification of both Wubei outcomes

**Files:**
- Inspect only: `HOI4_LOG.txt`

**Interfaces:**
- Consumes: completed implementation.
- Produces: manual evidence that both paths load, progress, and unify correctly.

- [ ] **Step 1: Verify the exile path**

Start SIC with the Shuntian exile flag, complete the route with console assistance, use enough decisions to reach integration 80, and complete national unification.

Expected: only “接纳顺天流亡者” is selectable; the final country is “大明军政国”; event 1039 then news 1041 fires; the exile-path final spirit is present.

- [ ] **Step 2: Verify the collaboration path**

Start SIC with STG existing and the in-power flag, complete the route and national unification.

Expected: only “南北武备合流” is selectable; the final country is also “大明军政国”; event 1040 then news 1042 fires; the collaboration-path final spirit is present.

- [ ] **Step 3: Inspect error output**

Search the game log for `SIC_wubei`, `SIC_daming_junzheng`, `TODSIC.103`, `TODSIC.104`, and `error`.

Expected: no missing localization, unknown modifier, invalid event, missing MIO trait, duplicate coordinate, or invalid cosmetic-tag error caused by this route.
