# SIC/SCG 在大明内战中的剧情与机制优化方案

> 状态：设计提案（未实现）。目标不是重写四川已有玩法，而是在「清政系治川试验 / 革命成功之后的制度、重建、全国统一」这一既有骨架上，把 SIC/SCG 与「大明内战」主线重新咬合，补齐叙事与系统耦合。

## 零、现状诊断（基于代码审查）

SIC/SCG 的本地玩法已经相当完整，问题不在四川内部，而在**与全国内战的耦合**：

1. **释放即脱钩。** SIC 由 `mingcivwar.80`（西南变局 1936.8.25）释放后，立即进入「产业崩溃 / 民众不满」的四川内部小游戏（`SIC.minzhong`、`SIC.gongye`），此后与全国内战主线几乎零互动；SCG 更是只在四川内部起义，不感知外面的内战进程。
2. **皇统叙事断裂。** SIC 有 `SIC_zunhuangtaojian`（尊皇讨奸）、`SIC_yonglizhengtong`（永奉正朔）、终局国号「大明君宪帝国」，但「尊的皇是谁」在代码里没有任何承接：昌德皇帝中风、太子遇刺（`mingcivwar.46`）、太孙朱喜钲摄政这条全国主线，SIC 完全不参与。
3. **清政系中央—四川无联动。** 中央清政系（领袖宋教仁，`MNG_party_5_leader`）是 MNG 的议会派系，SIC 是清政系的四川基地，但两者除了共用「清政系」三个字外没有任何机制/剧情连接。
4. **谈判对象只有两方。** `MNG_SIC_hebing_*` / `MNG_SCG_hebing_*` 只覆盖 ROC（共和国军）与 SRC（东北红军）；`TOD_china_unified_for_ming_civil_war` 清单里的 MNG / STG / GOS / XBJ / XIN / GPS / MOB 都只能靠军事征服，统一路径单一。
5. **AI 权重是死的。** ROC 50/50、SRC 30/70 写死为 `ai_chance = { factor = … }`，不随意识形态亲缘、实力对比、关系、战争状态、内战态势变化。
6. **统一是一键胜利。** `MNG_chongjiandaming_decision` 只做 `set_cosmetic_tag` + `add_ideas` + 弹一个事件（`TODSIC.1010` / `TODSIC.1012`），没有制宪、承认、清算、国际反应等过程；「大明君宪帝国」与「中华社会主义共和国」的成立缺乏因果链与仪式感。
7. **SCG 与 SRC 的「两条社会主义路线」没有思想交锋。** 合并只是 30/70 的裸吞并（`mingcivwar.1118`→`1119`），没有「多党两院制 vs 一党先锋制」的路线之争叙事。

---

## 一、剧情优化方案（叙事咬合）

### P1　皇统线：让 SIC 的「尊皇」有具体对象

把 SIC 的合法性叙事挂到全国主线的皇帝/太子/太孙身上：

- **触发点复用 `mingcivwar.46`（太子遇刺 1936.12.20）与昌德中风/太孙摄政链。** 当这些事件发生时，SIC 收到镜像事件，进入「勤王/迎驾」叙事分叉：
  - **迎太孙/皇室入川**：获得最高正统，但被其他觊觎皇统的割据政权宣战（武备系、顺天系等）。
  - **另立宗室**：在川内找一个朱姓远支，正统较低、代价小。
  - **虚君立宪**：不依赖具体皇帝，以「大明法统」为象征（对应现有 `SIC_junquan_guanyu_xianfa` 军权入宪、`SIC_zerenneige` 责任内阁），正统中等但宪政进度更快。
- **太子遇刺真凶线**：SIC 作为清政系分支启动调查（同产工会？武备系？紫禁系？），调查结论影响与各阵营的关系值、以及后续谈判权重——把「清政系=文官宪政派」的形象立起来。
- **产出**：新增 `SIC.zhengtong`（正统）资源（见 M5），皇统分支决定其天花板与获取方式。

### P2　清政系中央—四川双线联动（宋教仁线）

- **议会斗争外溢**：MNG 侧「扶持/打击清政系」决策（`MNG_fuchiqingzhengxi` / `MNG_dajiqingzhengxi`）的结果通过事件回传给 SIC——中央清政系得势则 SIC 获得人才、经费、正统与海外声望；被清洗则触发「清政系南下」事件，宋教仁等人物入川（获得角色 + 引发中央与四川的敌意）。
- **宋教仁的角色弧**：利用其「1933 遇刺、身体欠佳」的设定，做一条「宪政导师入川—抱病主持四川基本法—病逝留下遗志」的情感线，与 `SIC_sichuan_jibenfa`（四川基本法）绑定，让一部法律背后站着一个具体的人。
- **产出**：新增角色与少量事件；不改变议会派系本体逻辑，仅加一条 SIC 侧接收链。

### P3　SCG 与 SRC/ROC 的意识形态路线叙事

- **SCG × SRC（社会主义内部路线之争）**：合并谈判改为「两条路线」事件链——SCG 的**多党两院制**（人民大会 + 政党会）对 SRC 的**一党先锋制**。合并结果分档：
  - SCG 主导：红军并入两院制，出现「军队进政党会」的争论。
  - SRC 主导：SCG 的两院制实验被压缩为「统一战线」。
  - 平局：成立联合的「全国人民代表会议」。
- **SCG × ROC（社会主义 vs 共和主义）**：谈判围绕「大同会理想 vs 阶级革命」展开，接受/破裂的文案不再只是通稿。
- **产出**：替换 `mingcivwar.1112`–`1123` 的裸吞并效果为带文案的分档事件，仍复用现有吞并/将领国籍整合效果（`SCG_Sichuan_integration_effect`）。

### P4　统一建国的仪式化（多阶段叙事）

把「改 tag + 一个事件」扩成 4 步，让建国像建国：

1. **制宪/建国大会**：SIC 为「全国制宪派大会」（`SIC_quanguo_zhixianpai_dahui` 已存在，往后续接），SCG 为「中华制宪代表大会」（`SCG_zhonghua_zhixian_dabiao_dahui`）。会上选宪法条款（中央集权 vs 地方自治、军队归属等），产出不同国家精神。
2. **宣布建国**：面对残余割据政权的「承认 vs 讨伐」二分——和平承认的获得附庸/吞并，拒绝的进入宣战。
3. **国际承认**：列强态度事件（明系阵营 vs 反明阵营），影响后续外交与稳定。
4. **政权巩固**：清算/整合残余、军队国家化、定都等收尾事件。
- **产出**：将 `MNG_chongjiandaming_decision` 的 `complete_effect` 拆成可续接的事件链（见 M4），SIC/SCG 分支各自有专属文案。

---

## 二、机制优化方案（系统耦合）

### M1　全局「内战态势」变量系统

新增一组只读态势变量/旗标，供 SIC/SCG 的决策门槛、AI 权重、事件分支引用：

- `MNG 是否仍存在 / 是否被灭 / 皇统是否断绝`
- `内战参战方数量 / 是否发生多方混战`
- `左翼阵营（SRC+SCG）与共和阵营（ROC）与保皇阵营的相对控制区`
- `列强（法/英/俄等）在华的介入状态`

实现：放一个 `common/scripted_triggers/` 里的态势触发器，或在 `on_actions` / 定期决策里维护 `global_event_target` 或全局变量；避免改动各割据政权本体。

### M2　多边谈判/整合机制（从 2 国泛化到 10 国）

把现有「接壤 + 未交战 + 邀请→接受/反邀/破裂→战争」的握手协议泛化到 `TOD_china_unified_for_ming_civil_war` 的全部 tag：

- **SIC（君宪/清政系）** 对保皇/温和政权（MNG 皇统存续时、GOS、XBJ、STG 中温和者）接受度高；对 ROC/SRC 接受度低。
- **SCG（社会主义）** 对 SRC 接受度最高，对 ROC 中等，对保皇政权低。
- 保留既有「同一时间只谈一场」的 `SIC_hebing_tanpan_jinxingzhong` / `SCG_hebing_tanpan_jinxingzhong` 锁与「双方均拒绝才开放战争」原则。
- **实现**：为每个目标 tag 生成一对邀请/讨伐决策（模板化复制现有 `MNG_SIC_hebing_*`），成功合并统一走 `SIC_Sichuan_integration_effect` / `SCG_Sichuan_integration_effect`，避免裸 `annex_country`。

### M3　动态 AI 谈判权重（替代固定 50/50、30/70）

在 `ai_chance` 里叠加修正（保留原 50/50、30/70 作为基线）：

- 意识形态亲缘：`government_ideology` 相同/相近 → 接受 +；
- 相对实力：我方 `army size` / `factories` 优势 → 对方接受 +（弱方更愿意并入）；
- 关系值：`opinion` 高低；
- 威胁：存在共同敌人 → 接受 +；
- 内战态势：发起方已控制更多割据政权（M1 变量）→ 接受 +。

这样 AI 不再机械地 50/50，而是随局势演化。

### M4　统一决议多阶段化（替代一键胜利）

- 保留 `MNG_chongjiandaming_decision` 作为「门槛 + 触发」入口（已要求 `SIC_daming_junxian_ready` / `SCG_quanguo_xianfa_ready`），但把 `complete_effect` 里的 `set_cosmetic_tag + add_ideas + 单事件` 改为触发一个**多阶段国家事件链**（P4）。
- 每一阶段提供一个带 `ai_chance` 的分支，产出不同 `add_ideas` / 稳定度 / 军队国家化效果，形成「同样的统一，不同的国体」。
- 终局仍落在 `MNG_chongjiandaming_decision`，不新增第二个统一入口（遵守既有「不绕过路线」约束）。

### M5　SIC「正统」与 SCG「革命合法性」资源

- **SIC.zhengtong（正统）**：来源 = 皇统分支（P1）+ 清政系改革完成度（复用 `SIC.qingzhengxi` / `SIC.xianzheng` 阈值）+ 中央清政系联动（P2）。用途 = 统一谈判接受度加成、建国稳定度、对外宣称成本。
- **SCG.geminghefaxing（革命合法性）**：来源 = 重建完成度（复用 `SCG.chongjian`）+ 群众支持 + 两院授权（复用 `SCG.renmin_shouquan` / `SCG.dangji_xietiao`）。用途同上。
- **实现原则**：不新增无意义变量堆叠，优先从现有 5 个变量（`qingzhengxi`/`xianzheng`/`renmin_shouquan`/`dangji_xietiao`/`chongjian`）派生，`zhengtong`/`geminghefaxing` 只作为「统一阶段」的聚合显示与门槛。

### M6　内战 ↔ 四川双向耦合

打破「四川是孤岛」：

- **内战 → 四川**：
  - 多方混战（M1）→ 四川军需订单（经济机会）+ 流民涌入（`SIC.minzhong` 上升 / SCG 安置压力）。
  - MNG 中央崩溃 → SIC 失去朝贡与中央财政（财政减益）但获得外交自主权（谈判解锁）。
  - 邻省政权被吞并 → 难民潮 / 军事压力 / 扩张窗口三选一事件。
- **四川 → 内战**：
  - SIC 完成「四川模式」→ 清政系在全国声望上升，反过来影响中央议会派系与谈判接受度。
  - SCG 革命成功 → 左翼阵营获得「四川根据地」，SRC 与 SCG 的路线之争被摆上台面（P3）。
- **实现**：在 `mingcivwar` / `TODSIC` 事件里加少量 `trigger = { has_global_flag … }` 回传，成本低、叙事收益高。

### M7　SIC/SCG 特色终局变体

统一不再只有一个结局：

- **SIC**：
  - 「大明君宪帝国」——保留皇统 + 责任内阁 + 议会（现行）；
  - 「中华君宪共和国」（可选变体）——皇统断绝时，清政系转共和，虚君制走向废君共和。
- **SCG**：
  - 「中华社会主义共和国（两院制）」——SCG 主导合并（现行）；
  - 「中华人民共和国（一元制）」——SRC 主导合并，两院制被一元人民代表制取代。
- **实现**：在 `set_cosmetic_tag` 处按旗标分档 + 不同 `add_ideas` + 不同建国事件，复用现有 cosmetic tag 体系。

---

## 三、实施优先级与文件映射

### 优先级

- **Phase 1（低风险 / 高叙事收益，先做）**：M3 动态权重、P1 皇统线、P2 宋教仁线、M6 内战→四川单向回传。
- **Phase 2（中风险 / 系统收益）**：M5 正统/合法性资源、M2 多边谈判泛化、P3 路线之争叙事。
- **Phase 3（高风险 / 重构）**：M4 + P4 统一决议多阶段化、M7 特色终局变体。

### 文件映射

| 内容 | 主要文件 |
|---|---|
| P1 皇统线 / P2 清政系联动 / M6 回传 | `events/mingcivwar.txt`、`events/SiChuan.txt`（`TODSIC` 命名空间）、`events/mng.txt`（`ming_event`） |
| P3 路线之争 / P4 建国 / M7 终局 | `events/mingcivwar.txt`（替换 `1112`–`1123` 裸吞并）、`events/SiChuan.txt`（`TODSIC.1010`/`1012` 扩链） |
| M2 多边谈判 / M4 统一决议 | `common/decisions/MNG.txt`、`common/decisions/categories/MNG.txt` |
| M1 态势 / M5 资源派生 | `common/scripted_triggers/SIC_SCG_unification.txt`、`common/scripted_effects/SIC_chuanneijushi_scripted_effects.txt`、`common/scripted_effects/SCG_bicameral_effects.txt` |
| 国策门槛接入 | `common/national_focus/chuanyudifangsi.txt`、`common/national_focus/sichuangemingzhengfu.txt` |
| 本地化 | `localisation/simp_chinese/TOD_SIC_l_simp_chinese.yml`、`TOD_SCG_l_simp_chinese.yml`、`TOD_Ming_l_simp_chinese.yml`、`TOD_MNG_civwar_l_simp_chinese.yml` |
| 校验 | `tests/validate_sic_scg_constitutional_routes.py` |

---

## 四、约束与风险

- **不触碰受保护内容**：SIC 产业崩溃/民众不满/危机决议/川内 GUI、SCG 成都起义/地区起义/OOB/全川内战与革命胜利判定、`(25,1)` 阶段替换，一律不改（沿用 `2026-08-12` 规格的受保护边界）。
- **国策只向下连线、复用既有图标**，不新增美术资源。
- **单一统一入口**：所有建国仍经 `MNG_chongjiandaming_decision`，M4 只做「门槛后的事件链」，不新增第二条统一路径。
- **M2 泛化需防状态泄漏**：每个目标 tag 独立「谈判破裂」旗标，并复用既有 `*_hebing_tanpan_jinxingzhong` 互斥锁，避免并发谈判脏状态。
- **AI 权重改造不破坏既有契约**：ROC 50/50、SRC 30/70 作为基线保留，动态修正只做增量，静态校验器继续断言基线存在。
- 全程不提交、不推送、不上传。
