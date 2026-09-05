# Sichuan Focus Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reposition the new SIC and SCG political routes into collision-free left-hand lanes and replace their generic icons with existing, topic-appropriate icons.

**Architecture:** Keep every effect, prerequisite, cost, and availability condition unchanged. Extend the existing static validator with an exact focus-layout contract, then change only the `x`, `y`, and `icon` fields in the two focus files. The validator will confirm that no configured coordinate is shared by an original focus and that every new prerequisite line points downward.

**Tech Stack:** Hearts of Iron IV Clausewitz focus-tree definitions and the Python standard-library static validator.

## Global Constraints

- SIC route centre: `x = 7`; SCG route centre: `x = 6`.
- All newly added child nodes must have a greater `y` coordinate than every direct prerequisite.
- Reuse existing GFX icons; do not add image files or GFX definitions.
- Do not change effects, prerequisites, costs, availability, localisation, decision logic, tags, events, or AI weights.
- Do not stage, commit, or upload any files.

---

### Task 1: Add collision and direction regression checks

**Files:**
- Modify: `tests/validate_sic_scg_constitutional_routes.py`

**Interfaces:**
- Consumes: focus blocks from `common/national_focus/chuanyudifangsi.txt` and `common/national_focus/sichuangemingzhengfu.txt`.
- Produces: `focus_block()` and `FOCUS_LAYOUT_REQUIREMENTS`, which verify exact coordinates, selected icon identifiers, coordinate uniqueness, and downward prerequisite direction.

- [ ] **Step 1: Write the failing layout contract**

```python
FOCUS_LAYOUT_REQUIREMENTS = (
    (SIC_FOCUS, "SIC_qingzhengxi_sichuan", 7, 7, "GFX_focus_generic_bastion_of_democracy"),
    (SIC_FOCUS, "SIC_daming_lixian_guo", 7, 18, "GFX_focus_generic_bastion_of_democracy"),
    (SCG_FOCUS, "SCG_geminghou_diyici_huiyi", 6, 7, "GFX_goal_generic_propaganda"),
    (SCG_FOCUS, "SCG_zhonghua_shehuizhuyi_gongheguo", 6, 17, "GFX_focus_generic_bastion_of_democracy"),
)
```

- [ ] **Step 2: Run the validator before changing focus definitions**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: FAIL because the existing national-route coordinates are at `x = 13–15, y = 9–13` and do not satisfy the collision-free layout contract.

- [ ] **Step 3: Add focus-block extraction and direction checks**

```python
def focus_block(content: str, focus_id: str) -> str:
    start = content.index(f"id = {focus_id}")
    opening = content.rfind("focus = {", 0, start)
    depth = 0
    for index in range(opening, len(content)):
        depth += content[index] == "{"
        depth -= content[index] == "}"
        if depth == 0 and index > opening:
            return content[opening : index + 1]
    raise ValueError(f"unterminated focus block: {focus_id}")
```

- [ ] **Step 4: Run the validator and preserve the expected failure**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: FAIL only for the newly added layout contract, proving that it detects the old coordinates before the focus files are changed.

### Task 2: Reposition and retheme the SIC route

**Files:**
- Modify: `common/national_focus/chuanyudifangsi.txt:1557-1805`
- Test: `tests/validate_sic_scg_constitutional_routes.py`

**Interfaces:**
- Consumes: SIC coordinate and icon entries in `FOCUS_LAYOUT_REQUIREMENTS`.
- Produces: a downward SIC route from `(7, 7)` through `(7, 18)` without any node overlap in the existing tree.

- [ ] **Step 1: Set the SIC coordinates**

```text
7,7 → 5/9,8 → 5/9,9 → 5,10 → 7,11 → 5/9,12 → 7,13
→ 7,14 → 7,15 → 5/9,16 → 7,17 → 7,18
```

- [ ] **Step 2: Assign existing icons by subject**

```text
制度与宪法: GFX_focus_generic_bastion_of_democracy
预算与关税: GFX_goal_generic_positive_trade_relations
土地: GFX_goal_generic_construct_civ_factory
军队: GFX_focus_generic_military_mission / GFX_goal_generic_army_cooperation
宣言与责任政府: GFX_goal_generic_propaganda / GFX_goal_generic_political_pressure
会议与统一: GFX_goal_generic_national_unity
```

- [ ] **Step 3: Run the targeted regression test**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: SIC layout and existing constitutional-route checks pass.

### Task 3: Reposition and retheme the SCG route

**Files:**
- Modify: `common/national_focus/sichuangemingzhengfu.txt:1291-1499`
- Test: `tests/validate_sic_scg_constitutional_routes.py`

**Interfaces:**
- Consumes: SCG coordinate and icon entries in `FOCUS_LAYOUT_REQUIREMENTS`.
- Produces: a downward SCG route from `(6, 7)` through `(6, 17)` without any node overlap in the existing tree.

- [ ] **Step 1: Set the SCG coordinates**

```text
6,7 → 6,8 → 4/8,9 → 6,10 → 6,11 → 6,12
→ 4/8,13 → 6,14 → 6,15 → 6,16 → 6,17
```

- [ ] **Step 2: Assign existing icons by subject**

```text
会议与政治动员: GFX_goal_generic_propaganda / GFX_goal_generic_political_pressure
两院、宪法与终局: GFX_focus_generic_bastion_of_democracy
重建: GFX_goal_generic_construct_civ_factory
联络: GFX_goal_generic_positive_trade_relations
人民军: GFX_focus_generic_military_mission
制宪大会: GFX_goal_generic_national_unity
```

- [ ] **Step 3: Run the targeted regression test**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: SCG layout and existing constitutional-route checks pass.

### Task 4: Validate no overlaps and no upward links

**Files:**
- Modify: `tests/validate_sic_scg_constitutional_routes.py`
- Verify: `common/national_focus/chuanyudifangsi.txt`
- Verify: `common/national_focus/sichuangemingzhengfu.txt`

**Interfaces:**
- Consumes: final focus coordinates, icon values, and prerequisite declarations.
- Produces: verified Clausewitz files with no layout collision or upward new-route connection.

- [ ] **Step 1: Complete the exact coordinate/icon contract for all 29 new focuses**

```python
for path, focus_id, x, y, icon in FOCUS_LAYOUT_REQUIREMENTS:
    block = focus_block(path.read_text(encoding="utf-8-sig"), focus_id)
    assert f"x = {x}" in block
    assert f"y = {y}" in block
    assert f"icon = {icon}" in block
```

- [ ] **Step 2: Run complete verification**

Run: `python tests/validate_sic_scg_constitutional_routes.py`

Expected: `Sichuan constitutional-route validation passed.`

- [ ] **Step 3: Check whitespace and staged state**

Run: `git diff --check -- common/national_focus/chuanyudifangsi.txt common/national_focus/sichuangemingzhengfu.txt tests/validate_sic_scg_constitutional_routes.py`

Expected: no whitespace errors; no touched file is staged.
