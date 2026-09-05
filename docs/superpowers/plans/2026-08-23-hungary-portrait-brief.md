# Hungary Portrait and Art Brief Workbook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Deliver a desktop Excel workbook that lets the art team see every Hungary country-leader portrait requiring conversion and every removed Czech copied commander portrait, together with a replacement brief for a distinctly independent Danubian Hungarian armed forces.

**Architecture:** Build a standalone `.xlsx` from local mod scripts and assets. A small in-workspace JavaScript builder inventories character portrait references, resolves only existing local textures, and supplies structured rows to `@oai/artifact-tool`. The workbook embeds source thumbnails rather than hyperlinking paths, so it remains usable when sent to art. It does not edit source art or manufacture replacement portraits.

**Tech Stack:** Node.js bundled with Codex; `@oai/artifact-tool`; local image metadata/thumbnail support from the workspace dependencies; Excel `.xlsx`; rendered visual verification.

**Spec:** `docs/superpowers/specs/2026-08-23-hungary-content-and-portrait-overhaul-design.md`

## Global constraints

- Use the `spreadsheets:Spreadsheets` skill and its required `@oai/artifact-tool` workflow; do not use `openpyxl`, `pandas`, or another library to create the workbook.
- Before authoring: load workspace dependencies, select an appropriate workbook template through the available template-picker tool, read the required spreadsheet API quick-start and style guide in full, and mark the artifact operation started.
- The only deliverable write outside the mod is `C:\Users\wusiyi\Desktop\匈牙利人物肖像与将领重做清单.xlsx`; verify that the Desktop path exists first.
- Embed only local source images that actually resolve. For missing/unreadable assets, write the exact source path and a red `无法嵌入` status; never substitute a web image.
- Source images are a handoff reference, not replacement art. Keep their original aspect ratio and mark PNG/JPG country-leader images as `需转 DDS` rather than calling them in-game proof of a script error.
- Do not commit the user-facing workbook. Keep any temporary build artifacts outside source directories or delete only the named temporary folder after successful export.

---

## Task 1: Create a reproducible portrait inventory

**Files:**

- Read: `common/characters/HUN.txt`
- Read: `interface/HUN_pictures.gfx`
- Read: `D:\Game\Hearts of Iron IV\interface\*.gfx` as needed to resolve base-game GFX aliases
- Read: `gfx/leaders/HUN/*`
- Create: temporary builder under `outputs/hungary_portrait_brief/`

- [ ] **Step 1: Add an inventory assertion before workbook authoring.**

  Build a data-only check or direct preflight that emits the 11 country-leader source portraits with direct non-DDS paths: Kálmán Darányi, János Zichy, Archduke Joseph August, István Tisza, István Bethlen, Mihály Károlyi, János Vázsonyi, Károly Peyer, Tibor Eckhardt-Pozsonyi, György Lukács, and Tibor Szamuely. Confirm Béla Kun’s `.dds` is excluded from this conversion list.

- [ ] **Step 2: Run the preflight and inspect RED conditions.**

  Confirm every listed path either exists and can be embedded, or is explicitly marked as missing with its source path. Confirm the copied Czech roster extracted from the active scripts matches the removals in the content-overhaul plan.

- [ ] **Step 3: Resolve source thumbnails deterministically.**

  For each non-DDS leader path, use its literal local file. For removed Czech character entries, resolve their current large portrait GFX alias through local `.gfx` files; if it resolves to a DDS that the spreadsheet renderer cannot embed, create a temporary PNG preview from that local source while keeping the original DDS path in the workbook. Store the original path, preview path, dimensions, format, alpha/transparency observation, and a `可嵌入`/`无法嵌入` result in the inventory table.

## Task 2: Build a four-sheet art handoff workbook

**Files:**

- Create: temporary builder under `outputs/hungary_portrait_brief/`
- Create: `C:\Users\wusiyi\Desktop\匈牙利人物肖像与将领重做清单.xlsx`

- [ ] **Step 1: Start the mandated spreadsheet workflow.**

  Call `codex_app__load_workspace_dependencies`; load `@oai/artifact-tool` from the returned runtime. Use the available template picker to list and choose a suitable multi-sheet reference-table template. Read the spreadsheet skill’s `artifact_tool_docs/API_QUICK_START.md` and `style_guidelines.md` in full. Run `mark_artifact_operation_started.mjs` before the first workbook write.

- [ ] **Step 2: Construct the workbook with readable defaults.**

  Use one dark-green title band, Hungarian red-white-green accents, frozen header rows, filters, wrapped text, sensible widths, and no filler title sections. Use formula-free data tables unless a formula adds genuine value. Include four sheets exactly as follows:

  1. **肖像问题总表** — the 11 leader conversion records plus every removed Czech copied commander portrait, with columns: 分类, 角色名, 当前角色/来源, 原图预览, 原文件/GFX, 当前格式, 尺寸, 问题等级, 需要美工处理, 状态.
  2. **国家领导人** — one brief per country leader: ideology route, portrait usage context, direct source thumbnail, required DDS deliverable, and visual direction.
  3. **军队将领重做** — two grouped sections: retained native command roster (Lakatos, Hindy, Beregfy, Veress, Feketehalmy-Czeydner, Stromfeld, Szombathelyi, Sónyi, László, Werth) and removed Czech copied entries. Columns include gameplay role, alternate-history military identity, replacement visual brief, old copied thumbnail, and art status.
  4. **美工规格** — a concise production specification: required DDS format, dimensions to match the intended UI slot, transparent/opaque background instruction, filename convention, folder placement, no third-party national insignia, required visual motifs, and a priority queue.

  Make a row tall enough for each thumbnail. Embed previews from local images by file path/range using `@oai/artifact-tool`, preserving aspect ratio. Add conditional formatting to make `高` priority and `无法嵌入` visually obvious.

- [ ] **Step 3: Export and validate the initial workbook.**

  Export once to the Desktop target. Re-open with `artifact_tool` and inspect sheet names, headers, row counts, preview status, formulas (if any), and error scans. Confirm the workbook includes exactly the 11 non-DDS leader records and excludes Béla Kun from the conversion queue.

## Task 3: Render, visually inspect, and correct the workbook

**Files:**

- Verify: `C:\Users\wusiyi\Desktop\匈牙利人物肖像与将领重做清单.xlsx`

- [ ] **Step 1: Render every workbook sheet.**

  Use the supported spreadsheet rendering tool for all four sheets, producing temporary preview images at usable scale.

- [ ] **Step 2: Inspect the rendered images.**

  Check that headers are not clipped, thumbnails are visible and proportionate, row heights are sufficient, status colors remain legible, Chinese text wraps naturally, and no tables run off the page. Correct width/height/style defects in the builder and re-export if needed.

- [ ] **Step 3: Perform final structural verification.**

  Re-inspect with `artifact_tool` after the final export. Confirm no formula errors, no missing workbook sheets, no unresolved preview marked successful, and a clean mapping from each source record to the artist brief.

- [ ] **Step 4: Hand off the workbook.**

  Report the exact Desktop path using the required file citation format. State the number of country-leader conversion records, the number of removed copied commander records, and any local image files that could not be embedded.
