# 匈牙利外交与左翼民族路线补完 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 补齐匈牙利外交国策的实际效果，并完成左翼民族路线的整合/傀儡结局，同时保持东墙的默认 AI 倾向不变。

**Architecture:** 国策文件负责固定奖励和事件调用，事件文件负责玩家的外交与民族选择，一个匈牙利专用 scripted effect 集中清除民族纷争。Python unittest 静态校验锁定空效果、事件文本、傀儡语义和东墙 AI 不变量。

**Tech Stack:** Hearts of Iron IV Clausewitz 脚本、YAML 本地化、Python unittest。

**Spec:** docs/superpowers/specs/2026-08-25-hungary-diplomacy-and-left-nationalities-design.md

## Global Constraints

- 只修改匈牙利相关脚本、双语本地化与专项测试。
- HUN_dongqiang 的 AI 权重、创建阵营效果和既定成员逻辑完全不改。
- AI 的罗马尼亚、摩尔多瓦整合选项权重为 100；释放傀儡选项权重为 0。
- 释放仅使用 release_puppet 加 set_autonomy = { autonomy_state = autonomy_puppet }；不直接将州转交给独立国家。
- 外交效果不得让完成国策直接兼并其他国家。

---

### Task 1: 写入回归测试契约

**Files:**
- Modify: tests/validate_hungary_content.py
- Read: common/national_focus/hungary.txt、events/Hungary.txt、两份 Hungary localisation。

**Interfaces:**
- Consumes: focus_block() 和 braced_block_after()。
- Produces: test_diplomatic_focuses_have_concrete_effects、test_left_nationality_route_uses_player_only_puppet_settlements、test_east_wall_ai_contract_is_preserved。

- [ ] **Step 1: 写入失败的外交效果测试**

~~~python
required = (
    "HUN_junshihezuo", "HUN_duiyijiaoliu", "HUN_duohuikeluodiya",
    "HUN_ganyuyidali", "HUN_xiangnankuozhang", "HUN_pinggufaguo",
    "HUN_wengusaierweiya", "HUN_jierubaergan", "HUN_baerganbaquan",
    "HUN_kejihezuo", "HUN_junshijiaoliu",
)
for focus_id in required:
    self.assertNotRegex(
        focus_block(self.focus, focus_id),
        r"completion_reward\s*=\s*\{\s*\}",
    )
~~~

- [ ] **Step 2: 运行测试并确认失败**

Run: python tests/validate_hungary_content.py

Expected: 新外交测试失败，列出仍为空效果的国策。

- [ ] **Step 3: 写入失败的左翼与东墙 AI 测试**

左翼测试要求 HUN_zunzhongminzuzijue 不含 set_state_owner，并同时含 release_puppet = ROM、release_puppet = MOL 与两次 autonomy_state = autonomy_puppet。事件 TODhungary.28、.29 中整合选项必须为 factor = 100，傀儡选项必须为 factor = 0。东墙测试将 HUN_dongqiang 的 ai_will_do 规范化空白后断言为：

~~~python
"ai_will_do={base=100modifier={add=100}}"
~~~

- [ ] **Step 4: 运行测试并确认失败**

Run: python tests/validate_hungary_content.py

Expected: 左翼结算因旧州转交和 50/50 AI 权重失败；东墙 AI 契约通过。

- [ ] **Step 5: 提交测试契约**

~~~bash
git add tests/validate_hungary_content.py
git commit -m "test: define Hungary diplomacy and nationality contracts"
~~~

### Task 2: 实现左翼民族整合与玩家专属傀儡选择

**Files:**
- Create: common/scripted_effects/HUN_nationality_settlement_effects.txt
- Modify: common/national_focus/hungary.txt:1793-1853
- Modify: events/Hungary.txt:757-822
- Modify: localisation/english/TOD_Hungary_l_english.yml
- Modify: localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml
- Test: tests/validate_hungary_content.py

**Interfaces:**
- Consumes: 三个现有补偿 idea 与两个新增国家旗标 HUN_release_romania_as_puppet、HUN_release_moldova_as_puppet。
- Produces: HUN_clear_left_minority_disputes_effect、玩家主动选择的傀儡结算、完整双语文本。

- [ ] **Step 1: 运行左翼契约并确认失败**

Run: python tests/validate_hungary_content.py

Expected: 左翼测试失败，指出 set_state_owner 与 50/50 权重。

- [ ] **Step 2: 实现民族纷争清除 effect**

创建 country-scoped effect，遍历匈牙利拥有州并移除 HUN_shaoshuminzufenzheng 以及轻微、基本、勉强、严重、失控五个既有等级；不写入变量。

~~~txt
HUN_clear_left_minority_disputes_effect = {
    every_owned_state = {
        remove_dynamic_modifier = { modifier = HUN_shaoshuminzufenzheng }
    }
}
~~~

- [ ] **Step 3: 改写罗马尼亚、摩尔多瓦事件选择**

在 TODhungary.28、.29 中，第一项保留补偿 idea，AI 权重 100；第二项改为设置对应傀儡旗标，AI 权重 0。斯洛伐克事件只保留地方自治/整合结算，不添加自动释放。

- [ ] **Step 4: 在“尊重民族自决”进行最终结算**

调用清除 effect。补偿路线仅在由匈牙利拥有的指定州添加核心；玩家设置傀儡旗标且目标不存在时，分别执行：

~~~txt
release_puppet = ROM
set_autonomy = { target = ROM autonomy_state = autonomy_puppet }
~~~

摩尔多瓦使用同一模式。删除旧的 ROM = { set_state_owner = ... } 和 MOL = { set_state_owner = ... } 块。

- [ ] **Step 5: 补齐本地化并运行测试**

为三项民族处理的选择、傀儡结算和最终提示补齐双语文本。

Run: python tests/validate_hungary_content.py

Expected: 左翼结算与既有匈牙利专项测试全部通过。

- [ ] **Step 6: 提交左翼路线**

~~~bash
git add common/scripted_effects/HUN_nationality_settlement_effects.txt common/national_focus/hungary.txt events/Hungary.txt localisation/english/TOD_Hungary_l_english.yml localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml tests/validate_hungary_content.py
git commit -m "feat: complete Hungary left nationality settlement"
~~~

### Task 3: 实现外交线效果与叙事回应

**Files:**
- Modify: common/national_focus/hungary.txt:3096-3451
- Modify: events/Hungary.txt
- Modify: localisation/english/TOD_Hungary_l_english.yml
- Modify: localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml
- Test: tests/validate_hungary_content.py

**Interfaces:**
- Consumes: Task 1 的空效果和东墙 AI 契约。
- Produces: 十一个有实际后果的外交国策与 HUN.106、HUN.107、HUN.108 触发式事件；不修改 HUN_dongqiang。

- [ ] **Step 1: 运行外交契约并确认失败**

Run: python tests/validate_hungary_content.py

Expected: 外交空效果测试失败。

- [ ] **Step 2: 补齐西方与意大利支线**

- HUN_junshihezuo：陆军经验、一次陆军学说研究加成、HUN.106。
- HUN_duiyijiaoliu：意大利双向关系、政治点、HUN.107。
- HUN_duohuikeluodiya：仅对 103、109 州添加宣称。
- HUN_ganyuyidali：陆军经验与一次火炮或空军研究加成。

所有目标国家效果以存在和非战争条件保护。

- [ ] **Step 3: 补齐巴尔干与东方合作效果**

- HUN_xiangnankuozhang：对 105、108 州添加宣称与战争支持。
- HUN_pinggufaguo：法国关系与政治点。
- HUN_wengusaierweiya：稳定度与当地建设/整合收益。
- HUN_jierubaergan：调用 HUN.108。
- HUN_baerganbaquan：政治点、陆军经验、条件化巴尔干合作收益。
- HUN_kejihezuo：工业和电子研究加成。
- HUN_junshijiaoliu：陆军经验与学说研究加成。

不得使用 annex_country。不得改动 HUN_dongqiang 的任何字段。

- [ ] **Step 4: 添加三则触发式事件与本地化**

定义 HUN.106（奥匈军事代表团）、HUN.107（意大利合作提案）、HUN.108（巴尔干会议），均为 is_triggered_only = yes。每则有两项互斥、有限收益的选项；中英文各有标题、描述与两项选项文本。每则只由对应国策调用一次。

- [ ] **Step 5: 运行测试并确认通过**

Run: python tests/validate_hungary_content.py

Expected: 外交、左翼结算、事件本地化、东墙 AI 和既有全部匈牙利测试通过。

- [ ] **Step 6: 提交外交路线**

~~~bash
git add common/national_focus/hungary.txt events/Hungary.txt localisation/english/TOD_Hungary_l_english.yml localisation/simp_chinese/TOD_Hungary_l_simp_chinese.yml tests/validate_hungary_content.py
git commit -m "feat: enrich Hungary diplomatic routes"
~~~

### Task 4: 提交后验证与范围审计

**Files:**
- Verify: Tasks 2-3 的全部文件。

**Interfaces:**
- Consumes: 已实现的静态测试和 Git 提交。
- Produces: 可交接的本地分支状态。

- [ ] **Step 1: 运行完整专项测试**

Run: python tests/validate_hungary_content.py

Expected: 所有测试通过。

- [ ] **Step 2: 检查东墙与脚本空白**

~~~bash
git -c core.whitespace=cr-at-eol show --check --format= HEAD
python tests/validate_hungary_content.py
~~~

Expected: 两个命令退出码均为 0；东墙 AI 契约已由测试固定。

- [ ] **Step 3: 报告结果**

报告两个功能的游戏后果、AI 不释放约束、测试结果和提交哈希；说明未修改东墙 AI 倾向，也未触碰工作区的无关改动。
