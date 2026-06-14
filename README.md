# Product Ops Campaign Agent

A local file-based CLI tool that helps PO / Ops teams review campaign requests and look up setup instructions — without waiting for manual reviews.

---

## Purpose

Two agents in one CLI:

1. **Review Agent** — reads a campaign request (markdown file), extracts the 3 key points (Game Type, Task Triggers, Reward Types), checks each against the local KB allowlist, and outputs a clear split: *already supported* vs *needs PO confirm*.

2. **Setup Guide Agent** — answers natural-language questions about how to configure the campaign tool, pulling answers strictly from the local KB. Returns the answer plus the exact source section.

---

## MVP Scope — File-Only, No External Integrations

This MVP is intentionally constrained:

- **Local files only.** All knowledge comes from `data/kb/` markdown files.
- **No Confluence connection.** Request inputs are local markdown files in `data/samples/`.
- **No Jira connection.** No ticket creation or updates.
- **No external API calls.** No HTTP requests of any kind.
- **No production data.** All campaign request samples are mock data only.
- **No LLM inference.** Logic is deterministic keyword matching + scored keyword search.

---

## Repository Structure

```
hackathon_agent/
├── data/
│   ├── kb/
│   │   ├── kb_campaign_available.md     # Allowlist: supported game types, triggers, rewards
│   │   └── kb_setup_guide_content_v1.md # Setup instructions (A/B/C sections)
│   ├── samples/
│   │   └── campaign_request_sample_01.md # Mock campaign request
│   └── specs/
│       ├── spec_review_campaign_v1_1.md
│       └── spec_setup_guide_v1_final.md
├── src/
│   ├── app.py              # CLI entry point
│   ├── core/
│   │   └── kb_loader.py    # Reads KB files
│   ├── review/
│   │   ├── parser.py       # Parses request markdown
│   │   └── reviewer.py     # Allowlist checker + output formatter
│   └── setup_guide/
│       └── rag.py          # Keyword-based search over setup guide KB
└── tests/
    ├── test_review.py
    └── test_ask.py
```

---

## Local Setup

**Requirements:** Python 3.10+

```bash
# Clone and enter the repo
cd hackathon_agent

# Install test dependency (only needed for pytest)
pip install pytest
```

No other dependencies required.

---

## How to Run

### Review a campaign request

```bash
# Linux / macOS
python -m src.app review data/samples/campaign_request_sample_01.md

# PowerShell (Windows)
$env:PYTHONIOENCODING="utf-8"; python -m src.app review data/samples/campaign_request_sample_01.md
```

The agent reads the markdown request, checks Game Type / Task Triggers / Reward Types against the KB allowlist, and prints:

```
=== REVIEW: [DGS_260520_585] OTA - Lucky Wheel Vé hè 0đ ===
Tổng point: 10 | Đã hỗ trợ: 8 | Cần confirm: 2

--- ĐÃ HỖ TRỢ ---
[SCHEME] Game Type = lucky wheel ✅ (có trong allowlist)
[TASK] Task "Nạp điện thoại" ... → trigger = payment ✅ (keyword "nạp")
...

--- CẦN PO CONFIRM ---
1. [TASK] Task "Chụp màn hình chia sẻ campaign"
   Lý do: Không xác định được trigger — không khớp keyword nào
   Hỏi PO: Trigger cho task này đã available trên tool chưa?
```

### Ask a setup question

```bash
# Linux / macOS
python -m src.app ask "cách setup Game Type lucky wheel"

# PowerShell (Windows)
$env:PYTHONIOENCODING="utf-8"; python -m src.app ask "cách setup Game Type lucky wheel"
```

Other example questions:
```bash
python -m src.app ask "cách setup task trigger payment"
python -m src.app ask "tạo reward pool"
python -m src.app ask "setup leaderboard"
```

### Run the test suite

```bash
# Linux / macOS
python -m pytest

# PowerShell (Windows)
$env:PYTHONIOENCODING="utf-8"; python -m pytest
```

---

## Demo

```bash
# 1. Review the mock Lucky Wheel campaign request
python -m src.app review data/samples/campaign_request_sample_01.md

# 2. Ask how to set up Lucky Wheel
python -m src.app ask "cách setup Game Type lucky wheel"
```

**Expected review output highlights:**
- "Đặt vé máy bay hè" → classified as **payment** (keyword "đặt") ✅
- "Chụp màn hình chia sẻ campaign" → **CẦN PO CONFIRM** (no keyword match)
- Reward "vé" → **CẦN PO CONFIRM** (not in allowlist)

**Expected ask output:** Step-by-step Lucky Wheel setup guide with source `A1. [SCHEME] Lucky Wheel`.

---

## Current Limitations

- Request parser only supports the exact markdown table format defined in `data/samples/`.
- RAG uses keyword overlap scoring (no embeddings) — may miss paraphrased questions.
- Source references are KB section IDs, not live Confluence URLs.
- No interactive CLI / REPL mode; each invocation is stateless.
- Multi-intent questions are not split automatically.

---

## Future Optional Improvements

- Add more approved mock request samples to `data/samples/`.
- Improve markdown parser to support more request formats and field aliases.
- Add draft ticket text generator (pre-fill Jira fields from review output).
- Add campaign timeline checklist generator based on campaign start/end dates.
- Still no direct Confluence / Jira / API integration unless policy changes.
