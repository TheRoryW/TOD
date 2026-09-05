# SCG Post-Revolution Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild SCG’s post-revolution focus tree into symmetric economy, politics, and military branches while preserving the original 2×2 economic model and all military gameplay content.

**Architecture:** `SCG_gemingchenggong` remains the phase-switching root at `(25,1)` and directly fans out to branch axes X=11, X=25, and X=39. Economy and politics are extended with dedicated decision files, events, ideas, and one new revolution-prestige variable; military focus blocks are protected by normalized hashes so only coordinates and the root prerequisite may change. Cross-branch progression uses localized `available` conditions rather than prerequisite edges, preventing long lines across the focus tree.

**Tech Stack:** Hearts of Iron IV national focuses, ideas, decisions, events, scripted effects, dynamic modifiers, AI strategy, Simplified Chinese localization, Python static validation and JSON fixtures.

**Spec:** `docs/superpowers/specs/2026-08-24-sichuan-enterprises-wubei-scg-redesign-design.md`

## Global Constraints

- Preserve all content before `#革命成功` and preserve event `TODSIC.1005` and `common/decisions/SCG.txt` byte-for-byte.
- Preserve the ownership × agriculture 2×2 model and all eight existing outcome/follow-up focus IDs.
- Military focus names, icons, costs, effects, mutual exclusions, and existing available conditions are immutable; only coordinates and the new `SCG_gemingchenggong` root prerequisite may change.
- Branch axes are exactly X=11 economy, X=25 politics/diplomacy, X=39 military.
- New and existing post-revolution economy/politics focuses cost 5 (35 days); military costs remain unchanged.
- Cross-branch requirements use `available` plus localized custom tooltips, not cross-tree prerequisites.
- ROC/SRC merger behavior, adjacency, reverse invitation, double-refusal war gate, and base 50/50 and 30/70 weights remain unchanged.
- Reuse existing art; do not create image files.
- Preserve unrelated worktree changes; do not stage, commit, push, or upload Git changes.

---

### Task 1: Lock the approved layout and military content in tests

**Files:**
- Create: `tests/fixtures/scg_military_focus_contract.json`
- Create: `tests/validate_scg_postrevolution_redesign.py`

**Interfaces:**
- Consumes: helpers from `validate_sic_scg_constitutional_routes.py` and the current military focus blocks.
- Produces: exact coordinate, cost, branch-root, 2×2, event, decision, localization, and normalized military-content contracts.

- [ ] **Step 1: Save the normalized military hashes**

Create the JSON fixture with these exact values:

```json
{
  "SCG_chongzugemingjundui": "a68a61a49927ba7272288780b46643c0b588ed6c72039bf9d42a99b67c1fd119",
  "SCG_guanbingpingdeng": "2da5afc1f126d82ec7f8a25024c886da20de52156aca0144c10996c638db54a1",
  "SCG_huoliyanfa": "ff28b518dfe909e780ea5653b0e1286afce737e63f1cf46fc3f3041c33c87d89",
  "SCG_jianliminbingzhidu": "e0cc1d0ebd2af9d7593cb1af25532230c1f8d67f88d13c0d4a0c9bd897082a57",
  "SCG_jianlizhengwei": "2c00f1783f01f4f0be8fe284b993ffca6731dc0eb6015e2675b608216d0d7f24",
  "SCG_junduizhuanyehua": "49f0241f1ebc0c1b8dfb9332b80d67fe492951dca42cf9d373e3d6d076ffe75a",
  "SCG_kuodazhuangbeishengchan": "5a47551cc05b86d4676931719b516a4a85a230d70833e2ad29b3afb476cfe690",
  "SCG_minbingweifu": "c4a5df94e80649040482de61e4d14d3dcbd9964821e17a2f8bea22ff629cec8c",
  "SCG_minbingweizhu": "20091551520efaf68c7870fd4354b8920042c73cf1cea6ccc7d2416e10e6360f",
  "SCG_quanfuwuzhuang": "7830a965b06968a821964656dc04281922d737342711357268431ec958afbbd6",
  "SCG_renminjundui": "72f2cb59c4190cd7abaeaf4f27e867feeeeaa7a6ecf7d8380eb72527ca9ba772",
  "SCG_shenruqunzhong": "3b36cb97fd67b2b5fd9c8437a2dbe52aa15e82ef16278fa170050bafd40b88a4",
  "SCG_tishengchanpingongyi": "fc527391223cff4910e1e6706a4c9c2e0788440d25a1b47e5e926e450291d122",
  "SCG_tishengzhuangbeishuiping": "1a8ad58ebef704bbcff9a7b820b2f134aa0dd8385e20088b17af65c316ed8f2d",
  "SCG_yiliangqusheng": "ea25382faa28d2d4193c91a04bb230607328cf28f972241bb6af35bef5be99f2",
  "SCG_yizhiqusheng": "7e275dd5a4cd88c08806aac1a3a2000384336b6e769ff41223d0b4d029e540dc",
  "SCG_youqiubiying": "e7345d027d6f6819b6547e38237050a4ac3307a9e4802dfad57d4ccc78d46d6d",
  "SCG_zhuangbeixiafang": "a0fc2a0d0dff255b308392fd091dbfc69ab3551ef233ecc150331a7fce52f608",
  "SCG_ziligengsheng": "3547e3e01bcaf8f1ddc4bb8d728d591ff40bcd39700caa010385de89fbe2842c",
  "SCG_zizaowuqi": "3484de422b6fff66b9ac0acd0412a77323246259792c211db95922802bfdd68d"
}
```

- [ ] **Step 2: Write the failing post-revolution validator**

The validator must use this exact coordinate contract:

```python
ECONOMY_COORDS = {
    "SCG_sichuan_jingji_chongjian_weiyuanhui": (11, 2),
    "SCG_zuzhigonghui": (7, 3), "SCG_zuzhi_nonghui": (15, 3),
    "SCG_qiyegaizu": (6, 4), "SCG_gongrenzhichang": (8, 4),
    "SCG_wendingliangshigongji": (14, 4), "SCG_zuzhidangyuanxiaxiang": (16, 4),
    "SCG_wanquanguoyouhua": (6, 5), "SCG_gongsiheying": (8, 5),
    "SCG_tudigaige": (14, 5), "SCG_jitihuanongye": (16, 5),
    "SCG_shixingjihuajingji": (8, 6), "SCG_jiandaochalilun": (10, 6),
    "SCG_shehuizhuyigaizao": (12, 6), "SCG_xinjingjizhengce": (14, 6),
    "SCG_chanyelianzhenghe": (8, 7), "SCG_gongyefanbunongye": (10, 7),
    "SCG_nongyegongrengaizao": (12, 7), "SCG_hunhejingjitizhi": (14, 7),
    "SCG_sichuan_gongyehua_gangyao": (11, 8),
    "SCG_chengyu_gongye_zoulang": (9, 9), "SCG_chuannan_ziyuan_kaifa": (13, 9),
    "SCG_tianfu_gongye_tixi": (11, 10),
}

POLITICS_COORDS = {
    "SCG_geminghou_diyici_huiyi": (25, 2), "SCG_lianhezhengfu": (25, 3),
    "SCG_duodang_shehuizhuyi": (25, 4),
    "SCG_jianli_renmin_dahui": (23, 5), "SCG_jianli_zhengdanghui": (27, 5),
    "SCG_liangyuan_yishi_guize": (25, 6), "SCG_zeren_renminweiyuanhui": (25, 7),
    "SCG_sichuan_shehuizhuyi_xianfa": (25, 8),
    "SCG_renmin_zhangwo_sichuan": (21, 9), "SCG_chengdu_geming_waijiaoju": (29, 9),
    "SCG_changshe_difang_daibiao_zhidu": (21, 10),
    "SCG_quanguo_shehuizhuyi_zhengdang_huiyi": (29, 10),
    "SCG_quanguo_gongnong_lianluo": (23, 11), "SCG_shehuizhuyi_tongyi_zhanxian": (27, 11),
    "SCG_quanguo_gongtong_gangling": (25, 12), "SCG_quanguo_renminjun": (25, 13),
    "SCG_zhonghua_zhixian_dabiao_dahui": (25, 14),
    "SCG_zhonghua_shehuizhuyi_gongheguo": (25, 15),
}

MILITARY_COORDS = {
    "SCG_renminjundui": (39, 2),
    "SCG_guanbingpingdeng": (37, 3), "SCG_chongzugemingjundui": (39, 3), "SCG_jianlizhengwei": (41, 3),
    "SCG_jianliminbingzhidu": (35, 4), "SCG_junduizhuanyehua": (43, 4),
    "SCG_minbingweifu": (34, 5), "SCG_minbingweizhu": (36, 5),
    "SCG_yiliangqusheng": (42, 5), "SCG_yizhiqusheng": (44, 5),
    "SCG_youqiubiying": (33, 6), "SCG_ziligengsheng": (35, 6), "SCG_zhuangbeixiafang": (37, 6),
    "SCG_kuodazhuangbeishengchan": (41, 6), "SCG_huoliyanfa": (43, 6),
    "SCG_tishengzhuangbeishuiping": (45, 6),
    "SCG_shenruqunzhong": (34, 7), "SCG_zizaowuqi": (36, 7),
    "SCG_tishengchanpingongyi": (42, 7), "SCG_quanfuwuzhuang": (44, 7),
}
```

For all economy and politics IDs, assert `cost == 5`. For each row across all three maps, sort X values and fail if any adjacent difference is less than 2. Assert each branch root directly requires `SCG_gemingchenggong`.

Normalize military blocks by removing X/Y lines and the exact root prerequisite line, then compare SHA-256 hashes to the fixture. This makes any military reward, icon, cost, mutual exclusion, or existing condition change fail.

Assert the 2×2 pairs remain exactly:

```python
COMBINATIONS = {
    "SCG_shixingjihuajingji": ("SCG_wanquanguoyouhua", "SCG_jitihuanongye"),
    "SCG_jiandaochalilun": ("SCG_wanquanguoyouhua", "SCG_tudigaige"),
    "SCG_shehuizhuyigaizao": ("SCG_gongsiheying", "SCG_jitihuanongye"),
    "SCG_xinjingjizhengce": ("SCG_gongsiheying", "SCG_tudigaige"),
}
```

The validator must also require new focus/decision/event/localization IDs described in later tasks and assert `SCG_quanguo_gongtong_gangling` uses `available` references to economy and military milestones rather than prerequisite references to them.

- [ ] **Step 3: Run the validator and confirm it fails**

Run `python tests/validate_scg_postrevolution_redesign.py`.

Expected: the military normalized hashes pass before movement, while coordinate and missing-content checks fail.

---

### Task 2: Reposition the military branch without changing gameplay

**Files:**
- Modify: `common/national_focus/sichuangemingzhengfu.txt`
- Modify: `tests/validate_scg_postrevolution_redesign.py`

**Interfaces:**
- Consumes: the military coordinate map and hash fixture.
- Produces: a symmetric branch rooted at `(39,2)`.

- [ ] **Step 1: Add the revolution-success prerequisite to the root**

Add only this line to `SCG_renminjundui`:

```hoi4
prerequisite = { focus = SCG_gemingchenggong }
```

- [ ] **Step 2: Change every military X/Y pair to `MILITARY_COORDS`**

Do not alter any other line in the 20 military focus blocks.

- [ ] **Step 3: Run the military hash and coordinate checks**

Run `python tests/validate_scg_postrevolution_redesign.py`.

Expected: military hashes and coordinates pass; economy and politics remain failing.

---

### Task 3: Rebuild and strengthen the 2×2 economy branch

**Files:**
- Modify: `common/national_focus/sichuangemingzhengfu.txt`
- Modify: `common/ideas/SCG_idea.txt`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`

**Interfaces:**
- Consumes: existing ownership/agriculture focuses and `SCG.chongjian`.
- Produces: the economy coordinate map, four coherent model spirits, and three common industrialization focuses.

- [ ] **Step 1: Add the economy root and farmer organization focus**

Create `SCG_sichuan_jingji_chongjian_weiyuanhui` at `(11,2)` with `SCG_gemingchenggong` prerequisite. It unlocks the new economic decision category and grants 50 PP. Create `SCG_zuzhi_nonghui` at `(15,3)` with the economy root prerequisite; move `SCG_zuzhigonghui` to `(7,3)` and give it the same root.

Trigger `TODSIC.1050` from the economy root only if the political first-meeting focus has not yet fired it; use country flag `SCG_geminghou_shouci_huiyi_event_seen` to prevent duplication.

- [ ] **Step 2: Rewire and reposition all existing economic focuses**

Use `ECONOMY_COORDS`. Enterprise preparation focuses require `SCG_zuzhigonghui`; agriculture preparation focuses require `SCG_zuzhi_nonghui`. Preserve both ownership mutually exclusive choices and both agriculture mutually exclusive choices. Preserve the four combination prerequisites exactly as `COMBINATIONS`.

Remove the current constitution/two-house `available` gates from the four economic model and follow-up focuses so the branch can progress in parallel. The later industrialization outline provides the cross-branch gate.

- [ ] **Step 3: Consolidate temporary and final economic spirits**

At each model focus, remove all temporary ownership/agriculture ideas that are no longer meant to stack, then add one model idea. At each follow-up, replace the base model with its upgraded existing idea:

| Model focus | Base idea | Follow-up | Upgraded idea |
|---|---|---|---|
| 计划经济 | `SCG_jihuajingji` | 产业链整合 | `SCG_quanchanyelian` |
| 剪刀差理论 | `SCG_gongnongjiandaocha` | 工业反哺农业 | `SCG_nongyejixiehua` |
| 社会主义改造 | `SCG_shehuizhuyijinji` | 农业工人改造 | `SCG_chengxiangyitihua` |
| 新经济政策 | `SCG_zujianshichang` | 混合经济体制 | `SCG_shehuizhuyishichangjingji` |

Set the upgraded ideas to these exact displayed effects:

| Upgraded idea | Effects |
|---|---|
| `SCG_quanchanyelian` | factory output +15%, construction speed +10%, max efficiency +5%, consumer goods +5%, stability −5% |
| `SCG_nongyejixiehua` | military factory construction +20%, local resources +15%, factory output +5%, consumer goods +5%, stability −8% |
| `SCG_chengxiangyitihua` | factory output +8%, efficiency gain +15%, max efficiency +10%, construction speed +5%, stability +8% |
| `SCG_shehuizhuyishichangjingji` | civilian factory construction +20%, efficiency gain +10%, consumer goods −5%, factory output +5%, war support −5% |

Base ideas use half of each positive magnitude and the full thematic drawback. This ensures follow-ups are upgrades rather than a second permanent stack.

- [ ] **Step 4: Add the common industrialization tail**

Create `SCG_sichuan_gongyehua_gangyao` with an OR prerequisite over the four follow-up focuses. Its `available` block must require `SCG_liangyuan_yishi_guize` through a localized custom tooltip. It grants one research bonus for industry and 50 PP.

Create the two Y=9 focuses:

- `SCG_chengyu_gongye_zoulang`: add one infrastructure to controlled 830 and 831 and one civilian factory to whichever is controlled;
- `SCG_chuannan_ziyuan_kaifa`: add one infrastructure and one building slot to controlled 751 plus a 180-day local-resource bonus.

Create `SCG_tianfu_gongye_tixi` requiring both, with a localized `SCG.chongjian > 69` available condition. It adds one civilian and one military factory in controlled core states, 5% stability, and 100 PP.

- [ ] **Step 5: Add descriptions and event hooks**

Trigger ownership debate `TODSIC.1051`, agriculture debate `TODSIC.1052`, four model events 1053—1056, and worker/farmer coordination event 1057. Add or rewrite all affected focus descriptions to 100—180 Chinese characters.

- [ ] **Step 6: Run economy validation**

Run `python tests/validate_scg_postrevolution_redesign.py`.

Expected: the 2×2 map, coordinates, costs, model spirit references, and economic tail pass.

---

### Task 4: Add model-specific economic decisions

**Files:**
- Create: `common/decisions/categories/SCG_postwar_economy.txt`
- Create: `common/decisions/SCG_postwar_economy.txt`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`

**Interfaces:**
- Consumes: four economic-model focus flags and `SCG.chongjian`.
- Produces: category `SCG_shehuizhuyi_jingji_categories` and eight repeatable decisions.

- [ ] **Step 1: Create the category**

Allow only tag SCG. Show it after `SCG_sichuan_jingji_chongjian_weiyuanhui` and keep each decision visible only for its model focus.

- [ ] **Step 2: Add two decisions per model**

| Model | Decision | Cost / cooldown | Result |
|---|---|---|---|
| Plan | `SCG_zhiding_shengchan_zhibiao` | 40 PP / 120d | +5 reconstruction, 90d factory output +5% |
| Plan | `SCG_jizhong_zhongdian_gongye_lian` | 50 PP / 180d | +5 reconstruction, 90d construction +10% |
| Scissors | `SCG_tiaozheng_liangshi_shougoujia` | 35 PP / 120d | +5 people authorization, remove 2% stability loss risk |
| Scissors | `SCG_butie_nongye_jixie` | 50 PP / 180d | +5 reconstruction, 90d local resources +10% |
| Transformation | `SCG_kuoda_hezuoshe` | 40 PP / 120d | +4 reconstruction, +2% stability |
| Transformation | `SCG_jianli_gongren_jishu_weiyuanhui` | 50 PP / 180d | +5 reconstruction, one 50% industry research bonus |
| NEP | `SCG_fafang_shengchan_xukezheng` | 35 PP / 120d | +5 reconstruction, 90d civilian construction +10% |
| NEP | `SCG_jianguan_siren_ziben` | 45 PP / 150d | +4 party coordination, +25 PP after completion |

Every variable change calls `SCG_liangyuan_zhengzhi_gengxin = yes` so 0—100 bounds remain enforced.

- [ ] **Step 3: Add complete descriptions**

Every decision gets a `_desc` that identifies which model permits it, its social tradeoff, and its displayed duration/effect. No raw variable key may appear.

- [ ] **Step 4: Register and validate the new files**

Add both Clausewitz files to `CLAUSEWITZ_FILES` in the main Sichuan validator. Run both Sichuan validation commands.

Expected: no protected SCG uprising hash changes because `common/decisions/SCG.txt` remains untouched.

---

### Task 5: Rebuild the political and diplomatic branch

**Files:**
- Modify: `common/national_focus/sichuangemingzhengfu.txt`
- Modify: `common/scripted_effects/SCG_bicameral_effects.txt`
- Modify: `common/dynamic_modifiers/TOD_SCG_modifiers.txt`
- Modify: `common/ideas/SCG_idea.txt`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`

**Interfaces:**
- Consumes: existing two-house system and SCG nationwide-ready flag.
- Produces: the politics coordinate map, `SCG.geming_shengwang`, domestic/diplomatic sub-branches, and the cross-branch common-program gate.

- [ ] **Step 1: Move the existing institutional sequence**

Use `POLITICS_COORDS`. Rewire the top sequence to:

```text
革命成功 → 革命后的第一次会议 → 联合政府 → 多党社会主义
→ 人民大会 + 政党会 → 两院议事规则 → 责任人民委员会 → 四川社会主义宪法
```

Set every focus in this sequence to `cost = 5`. Move the existing `SCG_lianhezhengfu` event reward with the focus; do not leave it as an economy prerequisite.

- [ ] **Step 2: Initialize and clamp revolution prestige**

In `SCG_geminghou_diyici_huiyi`, set `SCG.geming_shengwang = 20` and trigger `TODSIC.1050` once. Extend `SCG_liangyuan_zhengzhi_gengxin` to clamp this variable to 0—100 without changing existing bounds or threshold effects for the other three variables.

- [ ] **Step 3: Add the domestic and diplomatic sub-branches**

Left branch:

- `SCG_renmin_zhangwo_sichuan`: retain its reconstruction requirement and effects;
- new `SCG_changshe_difang_daibiao_zhidu`: +5 people authorization, +5% stability, +5 prestige;
- move `SCG_quanguo_gongnong_lianluo` to `(23,11)`: +75 PP, +5 authorization, +5 prestige.

Right branch:

- new `SCG_chengdu_geming_waijiaoju`: unlock diplomacy category, +15 prestige, trigger event 1062;
- move `SCG_quanguo_shehuizhuyi_zhengdang_huiyi`: +5 party coordination, +10 prestige;
- new `SCG_shehuizhuyi_tongyi_zhanxian`: +5 authorization, +5 coordination, +10 prestige.

- [ ] **Step 4: Add the common program and national tail**

Create `SCG_quanguo_gongtong_gangling` with ordinary prerequisites from the two Y=11 political focuses. Add a localized `available` condition requiring:

- `SCG_sichuan_gongyehua_gangyao` completed;
- any one military terminal among `SCG_shenruqunzhong`, `SCG_zizaowuqi`, `SCG_tishengchanpingongyi`, `SCG_quanfuwuzhuang`;
- people authorization >59, party coordination >59, prestige >49.

Do not add economy or military focus prerequisites. The focus gives 100 PP, 5% stability, +10 prestige, and triggers event 1063.

Move `SCG_quanguo_renminjun`, `SCG_zhonghua_zhixian_dabiao_dahui`, and `SCG_zhonghua_shehuizhuyi_gongheguo` to Y=13—15 with cost 5. Keep `SCG_china_unified = yes` on the constituent assembly. The final focus only sets `SCG_quanguo_xianfa_ready`; it does not change the cosmetic tag.

- [ ] **Step 5: Add localization and visible threshold tooltips**

Add names/descriptions for all new focuses and tooltips for authorization, coordination, reconstruction, prestige, economy milestone, and military milestone gates. Rewrite short existing two-house/national descriptions to 100—180 Chinese characters.

- [ ] **Step 6: Run politics/layout validation**

Run `python tests/validate_scg_postrevolution_redesign.py` and the main Sichuan validator.

Expected: axes, costs, downward edges, no cross-tree prerequisite lines, and final readiness behavior pass.

---

### Task 6: Expand two-house and revolutionary-diplomacy decisions

**Files:**
- Modify: `common/decisions/SCG_bicameral_politics.txt`
- Create: `common/decisions/categories/SCG_revolutionary_diplomacy.txt`
- Create: `common/decisions/SCG_revolutionary_diplomacy.txt`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`

**Interfaces:**
- Consumes: four bounded SCG variables and the diplomacy focus.
- Produces: improved two-house descriptions, a budget-crisis event hook, and category `SCG_geming_waijiao_categories`.

- [ ] **Step 1: Add the budget-crisis hook to the existing session mission**

After the session timeout reduces authorization and coordination, trigger `TODSIC.1060` when either value is below 45 and country flag `SCG_liangyuan_yusuan_weiji_active` is absent. Set that flag before firing; event resolution clears it.

- [ ] **Step 2: Add four diplomacy decisions**

| Decision | Cost | Prestige | Effect |
|---|---:|---:|---|
| `SCG_zhengqu_zhengzhi_chengren` | 50 PP | −10 | relations +25 with non-hostile socialist countries, +25 PP after 45d |
| `SCG_yuanzhu_shehuizhuyi_youdang` | 40 PP | −10 | +5 party coordination, +2% stability after 30d |
| `SCG_paiqian_gongnong_daibiaotuan` | 35 PP | −8 | +5 people authorization, +5 prestige after 30d |
| `SCG_jianli_geming_lianluochu` | 60 PP | −15 | 180d improve-relations and ideology-defense national spirit |

Every decision is visible after `SCG_chengdu_geming_waijiaoju`, requires the listed prestige, has a 120—180 day cooldown, and calls the updater after variable changes.

- [ ] **Step 3: Preserve the negotiated-merger contract**

Do not duplicate ROC/SRC invitations in these new files. Add missing `_desc` localization to the existing MNG merger decisions and preserve adjacency, reverse invitation, double-refusal war gates, and base AI weights exactly.

- [ ] **Step 4: Register and validate the new files**

Add the new category and decision file to the main validator’s Clausewitz list. Run the post-revolution, constitutional-route, and merger checks.

Expected: no direct SCG ROC/SRC takeover decision is introduced outside the MNG civil-war category.

---

### Task 7: Add SCG events and complete localization polish

**Files:**
- Modify: `events/SiChuan.txt`
- Modify: `localisation/simp_chinese/TOD_SCG_l_simp_chinese.yml`
- Modify: `localisation/simp_chinese/TOD_MNG_civwar_l_simp_chinese.yml`
- Modify: `localisation/simp_chinese/TOD_Ming_l_simp_chinese.yml`

**Interfaces:**
- Consumes: economy model, two-house, diplomacy, common-program, and merger flags.
- Produces: `TODSIC.1050`—`TODSIC.1064`, polished SCG postwar descriptions, and complete merger response text.

- [ ] **Step 1: Add the fixed event allocation**

| ID | Event |
|---:|---|
| 1050 | 革命后的第一次会议 |
| 1051 | 工厂究竟属于谁 |
| 1052 | 土地与合作社之争 |
| 1053 | 计划经济方案确立 |
| 1054 | 城乡之间的剪刀差 |
| 1055 | 社会主义改造开始 |
| 1056 | 新经济政策获准试行 |
| 1057 | 工人委员会与农会的争执 |
| 1058 | 人民大会第一次开幕 |
| 1059 | 政党会中的反对票 |
| 1060 | 两院预算危机 |
| 1061 | 预算妥协案通过 |
| 1062 | 成都革命外交局成立 |
| 1063 | 全国共同纲领公布 |
| 1064 | 中华制宪代表大会 |

Use existing `TODSIC.1011` for the Sichuan socialist constitution publication and `TODSIC.1012` for final national founding. Do not create duplicate constitution/founding events.

- [ ] **Step 2: Give budget events mechanically distinct choices**

Event 1060 offers:

- prioritize People’s Assembly: authorization +8, coordination −4, PP −25;
- accept party compromise: coordination +8, authorization −4, stability +1%;
- convene a joint committee: both +4, PP −50, trigger 1061 after 7 days.

Every option clears `SCG_liangyuan_yusuan_weiji_active` and calls the updater.

- [ ] **Step 3: Complete event and legacy text**

Add `.t`, `.d`, and all option keys. Event descriptions target 130—220 Chinese characters. Audit every SCG post-revolution focus, decision, event, available tooltip, idea, and dynamic modifier; any narrative description below about 100 Chinese characters is rewritten to 100—180 characters. Short button labels and effect lists remain concise.

Polish the existing ROC/SRC merger invitation, refusal, reverse invitation, and double-refusal text without changing event IDs or effects.

- [ ] **Step 4: Run localization validation**

Run:

```powershell
python tests/validate_scg_postrevolution_redesign.py
python tests/validate_sic_scg_constitutional_routes.py
```

Expected: no missing focus `_desc`, decision `_desc`, event key, variable tooltip, malformed quote, or unintended duplicate localization key.

---

### Task 8: Update AI and perform full regression verification

**Files:**
- Modify: `common/ai_strategy/SCG.txt`
- Inspect: `HOI4_LOG.txt`

**Interfaces:**
- Consumes: completed focus/decision/event implementation.
- Produces: reachable AI paths for all four models and evidence that protected content and merger behavior remain intact.

- [ ] **Step 1: Add four economic AI plans**

Create four nonzero-weight plans corresponding to the four ownership/agriculture combinations. Each plan must prioritize its two choices, matching model focus, follow-up, industrialization outline, and industrial tail. Give all four equal base weight before situational modifiers so no model is unreachable.

- [ ] **Step 2: Add common political and military progression priorities**

Every plan prioritizes first meeting, coalition government, both houses, constitution, one military wing, industrialization outline, common program, and the national tail. The AI should run reconstruction and two-house decisions whenever a required variable is below its next threshold.

- [ ] **Step 3: Run all static validation commands**

Run:

```powershell
python tests/validate_scg_postrevolution_redesign.py
python tests/validate_sichuan_enterprises.py
python tests/validate_sic_wubei_route.py
python tests/validate_sic_scg_constitutional_routes.py
```

Expected: all exit 0. The protected opening hashes, military normalized hashes, 2×2 combinations, merger weights, and country-identity checks pass.

- [ ] **Step 4: Verify all four economic models in game**

Use four short console-assisted SCG runs. In each, complete one ownership choice, one agriculture choice, the expected model and follow-up, then verify the other three models are unavailable and the correct upgraded spirit/decisions appear.

- [ ] **Step 5: Verify branch layout and cross-gates**

Open the focus tree after revolution success.

Expected: economy, politics, and military roots are centered at 11/25/39; each branch is internally symmetric; no nodes overlap; no prerequisite line crosses between branches; common program displays localized unmet conditions until economy and military milestones are reached.

- [ ] **Step 6: Verify merger and national founding behavior**

Check one ROC and one SRC invitation. Confirm adjacency is required, rejection returns a reverse invitation, war is possible only after both sides refuse, and AI base chances remain 50/50 and 30/70. Complete nationwide unification and confirm only the MNG civil-war national-unification decision changes the country to 中华社会主义共和国.

- [ ] **Step 7: Inspect the game log**

Search for the new SCG focus, decision, event, idea, variable, and category prefixes plus `error`.

Expected: no unknown trigger/effect, invalid modifier, duplicate focus coordinate, missing localization, broken sprite, unresolved event target, or unbalanced script error caused by this implementation.
