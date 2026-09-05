# Sichuan Negotiated Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add neighbour-gated negotiated integration of ROC/SRC for SIC and SCG, and fire Sichuan national-unification events from the Ming civil-war unification decision.

**Architecture:** Two SIC/SCG-only categories in `MNG.txt` contain four invitation decisions and four refusal-gated war decisions. Each invitation starts a six-event handshake: target acceptance, target counter-offer, origin acceptance or rejection, target notification, and a mutual-refusal result. Per-route, per-target refusal flags gate the new war decisions. The existing `MNG_chongjiandaming_decision` remains the sole trigger for the SIC/SCG national-unification events.

**Tech Stack:** Hearts of Iron IV Clausewitz decisions, country events, localisation, Python standard-library static validator.

## Global Constraints

- Inviting country and target must be neighbours and not at war.
- ROC acceptance/refusal AI weights are 50/50; SRC acceptance/refusal AI weights are 30/70.
- A war decision against ROC or SRC is unavailable unless both sides have rejected the corresponding bilateral negotiation.
- No commit or remote upload is allowed for this work.

---

### Task 1: Extend the static validation contract

**Files:**
- Modify: `tests/validate_sic_scg_constitutional_routes.py`

- [x] Add expected SIC/SCG invitation IDs, all negotiation event IDs, MNG unification references, neighbour checks, and refusal-gated war decisions.
- [x] Run `python tests/validate_sic_scg_constitutional_routes.py` and verify failure before production changes.

### Task 2: Implement reciprocal integration decisions

**Files:**
- Modify: `common/decisions/MNG.txt`
- Modify: `common/decisions/SIC_constitutional_reform.txt`
- Modify: `common/decisions/SCG_bicameral_politics.txt`

- [x] Add SIC-only and SCG-only merger categories in `MNG.txt`, with four invitation decisions using `is_neighbor_of`, `country_exists`, and no-war conditions.
- [x] Replace the former direct ROC/SRC war decisions with four MNG-category war decisions gated by distinct mutual-refusal flags.
- [x] Run the static validator.

### Task 3: Implement event handshakes and texts

**Files:**
- Modify: `events/mingcivwar.txt`
- Modify: `localisation/simp_chinese/TOD_MNG_civwar_l_simp_chinese.yml`

- [x] Add six-event reciprocal handshakes for all four invitation pairs; successful options use `annex_country` and only the final mutual-refusal result sets the matching flag.
- [x] Apply 30/70 AI weights to SRC and 50/50 to ROC target responses.
- [x] Add every event title, description, and option text in Simplified Chinese.
- [x] Run the static validator and `git diff --check` on touched files.

### Task 4: Move national-unification event triggers

**Files:**
- Modify: `common/decisions/MNG.txt`
- Modify: `common/national_focus/chuanyudifangsi.txt`
- Modify: `common/national_focus/sichuangemingzhengfu.txt`

- [x] Add SIC and SCG branches to `MNG_chongjiandaming_decision`, setting their established cosmetic tags and firing `TODSIC.1010` or `TODSIC.1012`.
- [x] Remove direct firing of `TODSIC.1010` / `TODSIC.1012` from the two Sichuan end-state focuses.
- [x] Run the static validator, reference-integrity check, and targeted `git diff --check`.
