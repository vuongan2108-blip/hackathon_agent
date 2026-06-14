# Demo Checklist — Product Ops Campaign Agent (MVP 1 + 2 + 3)

---

## What This MVP Does

- **Review Agent (UC1):** Reads a local markdown campaign request, extracts 3 key points (Game Type, Task Triggers, Reward Types), checks each against the local KB allowlist, and outputs a structured review split — *ĐÃ HỖ TRỢ* vs *CẦN PO CONFIRM* — with a specific question for PO on each flagged item.
- **Setup Guide Agent (UC2):** Answers natural-language questions about campaign tool configuration by searching the local KB, returning the relevant steps plus an exact source section reference.
- **Ticket Content Generator (UC3):** Runs UC1 + UC2 internally, then drafts up to 4 coordination tickets (Biz / Design / PO / Ops) with SLAs and dependencies. Ops reviews and manually copy-pastes each ticket into Jira.
- **Local Demo UI (MVP 3):** Streamlit web UI exposing all three use cases in a browser with a download button for UC3 output.

## What This MVP Does NOT Do

- Does NOT connect to Confluence, Jira, or any external API.
- Does NOT read, write, or modify production data.
- Does NOT confirm, approve, or reject campaign requests — only classifies and flags.
- Does NOT use LLM inference or any cloud service.
- Does NOT send notifications or messages to any system.
- Does NOT write tickets to Jira — Ops reviews drafts and copy-pastes manually.
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

## UI Demo Flow (MVP 3 — Streamlit)

```bash
streamlit run ui_app.py
```

Steps:

1. Start the Streamlit app — browser opens at `http://localhost:8501`.
2. **UC1 tab:** Select `campaign_request_sample_01.md` → click **Run Review** → confirm ĐÃ HỖ TRỢ / CẦN PO CONFIRM split.
3. **UC2 tab:** Type `cách setup Game Type lucky wheel` → click **Ask** → confirm Lucky Wheel setup steps with Nguồn reference.
4. **UC3 tab:** Select `campaign_request_sample_01.md` → click **Generate Ticket Content** → confirm 4 tickets appear.
5. Click **Download as .txt** → save the file for offline review.
6. Confirm the UI says: *"Ops phải review nội dung bên dưới trước khi copy-paste sang Jira."*
7. Confirm the UI does **NOT** say "PO phải review trước khi copy-paste".

---

## Validation Points

Verify each of the following before demo:

| # | Check | Expected Result |
|---|---|---|
| 1 | Task "Đặt vé máy bay hè" | Classified as **payment** trigger using keyword **"đặt"** ✅ |
| 2 | Task "Chụp màn hình chia sẻ campaign" | Appears in **CẦN PO CONFIRM** — no keyword match |
| 3 | Reward type "vé" | Appears in **CẦN PO CONFIRM** — not in KB allowlist |
| 4 | Ask command source | Answer includes **"A1. [SCHEME] Lucky Wheel"** in Nguồn line |
| 5 | Test suite | `python -m pytest` → **88/88 passed** |
| 6 | UC3 PO ticket | Contains "Chụp màn hình" and "vé" — does NOT contain "Đặt vé máy bay hè" |
| 7 | UC3 Ops review wording | Output contains "Ops" + "review" + "copy-paste" |
| 8 | UI download button | Downloads `.txt` with Ops wording; no "PO must review" in label |

---

## Run Full Verification

```bash
# Review (UC1)
python -m src.app review data/samples/campaign_request_sample_01.md

# Ask (UC2)
python -m src.app ask "cách setup Game Type lucky wheel"

# Generate ticket content (UC3)
python -m src.app generate-ticket-content data/samples/campaign_request_sample_01.md

# Tests
python -m pytest -v

# UI (MVP 3)
streamlit run ui_app.py
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
