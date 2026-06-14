# Demo Checklist — Product Ops Campaign Agent (MVP)

---

## What This MVP Does

- **Review Agent:** Reads a local markdown campaign request, extracts 3 key points (Game Type, Task Triggers, Reward Types), checks each against the local KB allowlist, and outputs a structured review split — *ĐÃ HỖ TRỢ* vs *CẦN PO CONFIRM* — with a specific question for PO on each flagged item.
- **Setup Guide Agent:** Answers natural-language questions about campaign tool configuration by searching the local KB, returning the relevant steps plus an exact source section reference.

## What This MVP Does NOT Do

- Does NOT connect to Confluence, Jira, or any external API.
- Does NOT read, write, or modify production data.
- Does NOT confirm, approve, or reject campaign requests — only classifies and flags.
- Does NOT use LLM inference or any cloud service.
- Does NOT send notifications or messages to any system.
- All data is local, file-based, and mock-only.

---

## Demo Command 1 — Review Campaign Request

```bash
# Linux / macOS
python -m src.app review data/samples/campaign_request_sample_01.md

# PowerShell (Windows)
$env:PYTHONIOENCODING="utf-8"; python -m src.app review data/samples/campaign_request_sample_01.md
```

### Expected Output Summary

```
=== REVIEW: [DGS_260520_585] OTA - Lucky Wheel Vé hè 0đ ===
Tổng point: 10 | Đã hỗ trợ: 8 | Cần confirm: 2

--- ĐÃ HỖ TRỢ ---
[SCHEME] Game Type = lucky wheel ✅
[TASK] "Nạp điện thoại" → trigger = payment ✅ (keyword "nạp")
[TASK] "Điểm danh hàng ngày" → trigger = checkin ✅ (keyword "điểm danh")
[TASK] "Ghé thăm Fanpage Zalopay" → trigger = openlink ✅ (keyword "ghé thăm")
[TASK] "Mời bạn bè tham gia" → trigger = referral ✅ (keyword "mời")
[TASK] "Đặt vé máy bay hè" → trigger = payment ✅ (keyword "đặt")
[REWARD] voucher ✅
[REWARD] xu ✅

--- CẦN PO CONFIRM ---
1. [TASK] "Chụp màn hình chia sẻ campaign" — Không xác định được trigger
2. [REWARD] "vé" — Không có trong KB allowlist
```

Full captured output: `demo_outputs/review_output_sample.txt`

---

## Demo Command 2 — Setup Guide Q&A

```bash
# Linux / macOS
python -m src.app ask "cách setup Game Type lucky wheel"

# PowerShell (Windows)
$env:PYTHONIOENCODING="utf-8"; python -m src.app ask "cách setup Game Type lucky wheel"
```

### Expected Output Summary

- Returns Step 0 through Step 7 of Lucky Wheel setup (General Info, Mechanism, UI Config, Review & Create).
- Ends with: `**Nguồn:** https://events-tool.zalopay.vn/ — A1. [SCHEME] Lucky Wheel`

Full captured output: `demo_outputs/ask_output_sample.txt`

---

## Validation Points

Verify each of the following before demo:

| # | Check | Expected Result |
|---|---|---|
| 1 | Task "Đặt vé máy bay hè" | Classified as **payment** trigger using keyword **"đặt"** ✅ |
| 2 | Task "Chụp màn hình chia sẻ campaign" | Appears in **CẦN PO CONFIRM** — no keyword match |
| 3 | Reward type "vé" | Appears in **CẦN PO CONFIRM** — not in KB allowlist |
| 4 | Ask command source | Answer includes **"A1. [SCHEME] Lucky Wheel"** in Nguồn line |
| 5 | Test suite | `python -m pytest` → **49/49 passed** |

---

## Run Full Verification

```bash
# Review
python -m src.app review data/samples/campaign_request_sample_01.md

# Ask
python -m src.app ask "cách setup Game Type lucky wheel"

# Tests
python -m pytest -v
```

---

## Known Limitations

- Request parser supports only the fixed markdown table format used in `data/samples/`.
- RAG uses keyword overlap scoring (no embeddings) — rephrased or abbreviated questions may miss the right section.
- Source references are KB section IDs (e.g. `A1`), not live Confluence links.
- Single question per `ask` invocation; multi-intent questions are not split.
- No REPL / interactive mode — each CLI call is stateless.
- Duplicate root-level `.md` files exist in the repo root (unremovable filesystem artifact from initial extraction); they are not read by any code — canonical files are under `data/`.

---

## Suggested Next Improvements

- Add more approved mock request samples to `data/samples/`.
- Improve markdown parser to handle more request formats and field aliases.
- Add draft ticket text generator (pre-fill Jira fields from review output).
- Add campaign timeline checklist generator based on campaign start/end dates.
- Still no direct Confluence / Jira / API integration unless policy changes.
