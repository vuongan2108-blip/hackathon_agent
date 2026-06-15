# Final Demo Checklist — Product Ops Campaign Agent

---

## Pre-Demo Setup

### 1. Install dependencies

```bash
cd hackathon_agent
pip install -r requirements.txt
```

Expected: no errors. Installs `pytest` and `streamlit`.

### 2. Verify test suite

```bash
# Linux / macOS
python -m pytest

# PowerShell (Windows)
$env:PYTHONIOENCODING="utf-8"; python -m pytest
```

**Expected:** `133 passed` with no failures or errors.

### 3. Verify CLI commands

```bash
# UC1
python -m src.app review data/samples/campaign_request_sample_01.md

# UC2
python -m src.app ask "cách setup Game Type lucky wheel"

# UC3
python -m src.app generate-ticket-content data/samples/campaign_request_sample_01.md

# UC4
python -m src.app timeline data/samples/campaign_request_sample_01.md
```

See "Expected output" section below for what to look for.

### 4. Start the Streamlit UI

```bash
streamlit run ui_app.py
```

**Expected:** browser opens automatically at `http://localhost:8501`.
If it doesn't open, navigate there manually.

### 5. Confirm branch

```bash
git branch --show-current
```

**Expected:** `main`

---

## Expected Output — Quick Reference

### UC1 review

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
1. [TASK] "Chụp màn hình chia sẻ campaign" — no keyword match
2. [REWARD] "vé" — not in KB allowlist
```

### UC2 ask

```
**[SCHEME] Lucky Wheel**
Step 0 — Create: ...
Step 1 — General Info: ...
...
**Nguồn KB nội bộ:** A1. [SCHEME] Lucky Wheel
```

### UC3 generate-ticket-content

```
=== DRAFT CONFIRMATION TICKETS: ... ===
⚠️  Ops phải review nội dung bên dưới trước khi copy-paste sang Jira. ...

--- TICKET: BIZ ---
--- TICKET: DESIGN ---
--- TICKET: PRODUCT CONFIRMATION ---
--- TICKET: OPS ---

--- END OF DRAFT ---
Ops: review xong thì copy từng ticket vào Jira. ...
```

Also saves: `demo_outputs/generate_ticket_content_output_sample.txt`

---

## Validation Checklist

| # | Check | Command / Action | Expected |
|---|-------|-----------------|----------|
| 1 | Dependencies installed | `pip install -r requirements.txt` | No errors |
| 2 | Test suite | `python -m pytest` | 133 passed |
| 3 | UI syntax | `python -m py_compile ui_app.py` | No output (= OK) |
| 4 | UC1 review | CLI command above | 8 supported, 2 needs-confirm |
| 5 | UC2 ask | CLI command above | Steps + Nguồn A1 line |
| 6 | UC3 tickets | CLI command above | 4 ticket blocks + footer |
| 7 | Streamlit UI starts | `streamlit run ui_app.py` | Browser at :8501 |
| 8 | UC1 tab | Select file → Run Review | Same as CLI output |
| 9 | UC2 tab | Type question → Ask | Same as CLI output |
| 10 | UC3 tab | Select file → Generate | 4 tickets + download button |
| 11 | Download button | Click download | `.txt` file saved locally |
| 12 | Ops wording | Check UC3 output | "Ops phải review … copy-paste" |
| 13 | No PO wording | Check download label | Does NOT say "PO must review" |
| 14 | UC4 CLI | `python -m src.app timeline <file>` | Grid: 4 rows, Ops 3-track, review note |
| 15 | UC4 UI tab | UC4 tab → Generate Timeline | Markdown grid + download button |
| 16 | Branch | `git branch --show-current` | `main` |

---

## Troubleshooting

### Streamlit not installed

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Fix:**
```bash
pip install -r requirements.txt
```
or:
```bash
pip install streamlit
```

---

### Terminal encoding issue (Windows)

**Error:** `UnicodeEncodeError` or garbled Vietnamese characters

**Fix:** Always prefix commands with the encoding variable in PowerShell:
```powershell
$env:PYTHONIOENCODING="utf-8"; python -m src.app review data/samples/campaign_request_sample_01.md
```

---

### Port already in use

**Error:** `OSError: [Errno 48] Address already in use` or `Port 8501 is already in use`

**Fix:**
```bash
# Find and kill the process using port 8501
# macOS / Linux:
lsof -ti:8501 | xargs kill -9

# Windows PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess | Stop-Process -Force
```

Or start on a different port:
```bash
streamlit run ui_app.py --server.port 8502
```

---

### Browser does not open automatically

**Fix:** Navigate manually to `http://localhost:8501` in any browser.

---

### Git branch is not on main

**Error:** Wrong branch shown by `git branch --show-current`

**Fix:**
```bash
git checkout main
git pull origin main
```

---

### `src.app` not found

**Error:** `No module named src.app`

**Fix:** Make sure you are running commands from the `hackathon_agent/` directory (the repo root), not from inside `src/`:
```bash
cd hackathon_agent
python -m src.app review data/samples/campaign_request_sample_01.md
```

---

### Sample file not found

**Error:** `[ERROR] Request file not found: data/samples/campaign_request_sample_01.md`

**Fix:** Confirm the file exists:
```bash
ls data/samples/
```
If missing, check that you are in the correct directory or that the file was not accidentally deleted.

---

## What This Demo Does NOT Do

- Does NOT connect to Confluence, Jira, or any external API.
- Does NOT use production data — all campaign requests are mock data.
- Does NOT create or update any Jira ticket — Ops must copy-paste manually.
- Does NOT use LLM inference — logic is deterministic keyword matching.
- Does NOT send any notification or message to any system.
