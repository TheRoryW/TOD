# TOD 模组错误修复计划

## 背景：上一轮问题的修复状态（已核实）

**已修复**：`00_traits.txt` 的11处 `FR }`、SIC脚本缺括号、germany.txt 多余括号、海军学说缺括号、ideas_asia.gfx、LAF/ZHR/YZR units 括号、TSO/COE 已新建正确命名的本地化副本。

**未修复/部分修复**（列入本计划B部分）：6个尾空格本地化文件仍在、AFG/BRA 旧文件未合并删除、ENG_ideas/USA_South_idea/MES/MSR/USM_naval_mtg 仍缺1个 `}`、Portugual 文件缺BOM、空BoP文件仍在。

---

## A部分：修复本次日志错误（6类）

### A1. GFX_event_news_pic_overlay 找不到（新闻事件弹窗刷错）
**根因**：mod 的 `interface/eventwindow.gfx` 同名覆盖了原版文件，但里面删掉了这个 sprite 定义（贴图 `gfx/interface/event_news_pic_overlay.dds` 仍在原版，可用）。
**修复**：在 `interface/eventwindow.gfx` 的 spriteTypes 闭合 `}` 前（第50行 GFX_event_news_bg 之后）补：
```
spriteType = {
	name = "GFX_event_news_pic_overlay"
	texturefile = "gfx/interface/event_news_pic_overlay.dds"
}
```

### A2. GER.txt:351 promote_character 角色不存在
**根因**：`events/GER.txt` 第316行引用 `GER_Wilhelm_Pieck_1`、第351行引用 `GER_Wilhelm_Pieck_2`，都不存在；`common/characters/GER.txt:77` 只有 `GER_Wilhelm_Pieck`（带 vanguard_socialism_subtype 领袖角色，与事件 `set_politics = vanguard_socialism` 匹配）。
**修复**：两处引用统一改为 `GER_Wilhelm_Pieck`。

### A3. Louisiana.txt:197 无效 idea
**根因**：`FRL_consociationalism_will_fix_idea` 全 mod 未定义（Louisiana_ideas.txt 有 stub 占位区，漏写了这个）。
**修复**：在 `common/ideas/Louisiana_ideas.txt` stub 区补定义（温和正面 modifier：stability_weekly、political_power_gain、drift_defence_factor，picture 复用 FRL_political_crisis），并在 english + simp_chinese 的 FRL 本地化文件补 idea 名称条目。

### A4. mingcivwar.txt:974 transfer_units_fraction 国家不存在
**根因**：事件 mingcivwar.77 由 on_actions 定时396天触发且无 trigger 校验；明代内战链条未放出 ROC（大同会）时，`set_autonomy`/`transfer_units_fraction` 等 ROC 操作全部报错。
**修复**：把 option a 中所有依赖 ROC 存在的效果（set_autonomy、transfer_units_fraction、transfer_navy、add/transfer_state、cosmetic、load_oob、set_politics、set_popularities、inherit_technology）包进 `if = { limit = { exists = ROC } }`；`complete_national_focus` 和 `MNG_release_ROC` 保留在外。

### A5. 角色名生成失败（路易斯安那/关东招抚司/华南招抚司/明属东非）
**现状**：mod 已有 `common/names/TOD_missing_character_names.txt`（9/3新增，FRL/GPS/ROC/MEA 池已存在），但日志疑似修复后仍报错。
**修复**：(a) 对照原版 `common/names/00_names.txt` 校验文件结构（重点：surnames 是否需在 male 块内部，结构错了就改）；(b) 补 GJG（工具国）姓名池；(c) 防御性补 cosmetic 键池 `ROC_ming`/`huananzhaofusi`/`GPS_ming`（复制对应 tag 块）。

### A6. AI tried to post an invalid command: merge_navies
**结论**：全 mod 无脚本调用，属引擎级 AI 舰队合并被拒（常见于同名舰船/舰队不同海区），无直接脚本修复项。附带扫描 `history/units/` 海军 OOB 中同一 tag 内的重复舰名，发现则先报告再定。

---

## B部分：补完上一轮遗留

1. **括号**：`common/ideas/ENG_ideas.txt`、`USA_South_idea.txt` 末尾各补1个 `}`；`history/units/MES.txt`、`MSR.txt`、`USM_naval_mtg.txt` 末尾各补1个 `}`。
2. **本地化文件**：
   - ARG/HYD/PAR/UZB 4个尾空格文件重命名去掉空格（无副本冲突）
   - AFG：旧文件的8个key（阿富汗总督领）合并进 `TOD_AFG_l_english.yml` 后删旧文件
   - BRA：旧文件key已被新文件完整覆盖（实施时验证）后删旧文件
   - `TOD_TSO_l_english).yml` 的8个key合并进 `TOD_TSO_l_english.yml` 后删旧
   - `TOD_COE.yml` 的8个key合并进 `TOD_COE_l_english.yml` 后删旧
   - `TOD_Viceroyalty_of_Portugual_l_english.yml` 补 UTF-8 BOM
3. **删除空文件** `common/scripted_effects/TOD_BoP_GUI_Scripted_effects.txt`。

## 验证
- 所有改动文件重跑括号平衡检查（{ = }）
- 本地化合并后重跑重复key扫描，确认无丢失
- 列出全部变更清单供用户确认