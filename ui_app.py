"""
Product Ops Campaign Agent — Local Demo UI (MVP 3 + UC4)

Run:
    streamlit run ui_app.py

Four tabs:
    UC1 — Review Campaign Request
    UC2 — Setup Guide Q&A
    UC3 — Generate Ticket Content
    UC4 — Timeline Campaign Assistant
"""

from __future__ import annotations

import re
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

# ── Ensure repo root is on sys.path regardless of cwd ─────────────────────
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ── Sample file discovery ──────────────────────────────────────────────────
_SAMPLES_DIR = _ROOT / "data" / "samples"


def _list_samples() -> list[Path]:
    if not _SAMPLES_DIR.exists():
        return []
    return sorted(_SAMPLES_DIR.glob("*.md"))


# ── Core logic wrappers — lazy imports, mirror CLI exactly ─────────────────

def run_review_for_ui(sample_path: str) -> str:
    from src.review.reviewer import review_request, format_review  # noqa: PLC0415
    return format_review(review_request(sample_path))


def run_ask_for_ui(question: str) -> str:
    from src.setup_guide.rag import answer_question  # noqa: PLC0415
    return answer_question(question)


def run_ticket_generation_for_ui(sample_path: str) -> tuple[str, str]:
    """Returns (metadata, tickets_only). metadata for display; tickets for download."""
    from src.draft_confirmation.generator import generate_draft  # noqa: PLC0415
    result = generate_draft(sample_path)
    return result.render_metadata(), result.render()


def run_timeline_for_ui(sample_path: str) -> str:
    """Returns ASCII timeline text (used for .txt download)."""
    from src.timeline.generator import generate_timeline  # noqa: PLC0415
    return generate_timeline(sample_path).render()


def get_timeline_result_for_ui(sample_path: str):
    """Returns raw TimelineResult for Gantt rendering."""
    from src.timeline.generator import generate_timeline  # noqa: PLC0415
    return generate_timeline(sample_path)


# ── Helpers ────────────────────────────────────────────────────────────────

def _parse_dd_mm_yyyy(s: str):
    """Parse dd/mm/yyyy → date; returns None on failure."""
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except Exception:
        return None


def _short_campaign_name(name: str) -> str:
    """Shorten campaign_name for Gantt bar labels.

    '[DGS_260520_585] OTA - Lucky Wheel Vé hè 0đ'  →  'OTA Lucky Wheel'
    """
    s = re.sub(r"^\[[\w\s_\-]+\]\s*", "", name).strip()   # drop [CODE] prefix
    s = re.sub(r"\s*[-–—]\s*", " ", s).strip()  # normalise separators
    _filler = {"0đ", "vé", "ve", "hè", "he", "xuân", "mùa", "tết", "tet"}
    words = [w for w in s.split() if w.lower() not in _filler]
    result = " ".join(words[:3])
    return result if result else name[:24]


# ── CSS injection ──────────────────────────────────────────────────────────

def inject_app_css() -> None:
    """Fine-tune CSS on top of .streamlit/config.toml (which sets the base theme)."""
    st.markdown(
        """
<style>
/* ── Background ── */
.stApp,
section[data-testid="stMain"],
section[data-testid="stMain"] > div,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
}

/* ── Typography ── */
h1 { color: #111827 !important; font-weight: 700 !important; margin-bottom: 4px !important; }
h2 { color: #111827 !important; font-weight: 600 !important; }
h3 { color: #111827 !important; font-weight: 600 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #00B14F !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #00B14F !important;
}
.stTabs [data-baseweb="tab-border"] {
    background-color: #E6E8EB !important;
}

/* ── Primary buttons ── */
button[data-testid="baseButton-primary"] {
    background-color: #00B14F !important;
    border-color:     #00B14F !important;
    color:            #FFFFFF !important;
    border-radius:    8px     !important;
    font-weight:      500     !important;
}
button[data-testid="baseButton-primary"]:hover {
    background-color: #009940 !important;
    border-color:     #009940 !important;
}

/* ── Secondary / download buttons ── */
button[data-testid="baseButton-secondary"],
.stDownloadButton > button {
    border-radius: 8px      !important;
    border-color:  #E6E8EB  !important;
    color:         #374151  !important;
    font-weight:   500      !important;
}

/* ── Remove icons from alert/info/success/error boxes ── */
[data-testid="stAlert"] svg { display: none !important; }
[data-testid="stAlert"] { border-radius: 8px !important; }

/* ── Code blocks ── */
[data-testid="stCode"] {
    border-radius: 8px     !important;
    border:        1px solid #E6E8EB !important;
}
[data-testid="stCode"] pre {
    background-color: #F9FAFB !important;
}

/* ── Input / selectbox ── */
[data-testid="stTextInput"] input {
    border-radius: 8px     !important;
    border-color:  #E6E8EB !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border-radius: 8px     !important;
    border-color:  #E6E8EB !important;
}

/* ── Divider ── */
hr {
    border:     none !important;
    border-top: 1px solid #E6E8EB !important;
    margin:     12px 0 !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ── UI helper components ───────────────────────────────────────────────────

def render_status_box(message: str, kind: str = "success") -> str:
    """Return HTML for a clean inline status notification."""
    styles = {
        "success": ("#EAF8EF", "#00B14F", "#065F46"),
        "info":    ("#EAF2FF", "#0068FF", "#1E3A8A"),
        "neutral": ("#F3F4F6", "#E6E8EB", "#374151"),
    }
    bg, border, fg = styles.get(kind, styles["neutral"])
    return (
        f'<div style="background:{bg}; border:1px solid {border}; border-radius:8px; '
        f'padding:10px 16px; font-size:14px; color:{fg}; font-weight:500; line-height:1.4;">'
        f"{message}</div>"
    )


def render_info_card(message: str) -> str:
    """Return HTML for a friendly info/tips card (replaces warning boxes)."""
    return (
        '<div style="background:#EAF2FF; border:1px solid #C7DCFF; border-radius:8px; '
        f'padding:12px 16px; font-size:13px; color:#1E3A8A; line-height:1.6;">'
        f"{message}</div>"
    )


def render_uc4_summary_card(result) -> str:
    """Return HTML for the campaign summary card shown above the Gantt."""
    d = result.draft
    rows = [
        ("Campaign",    d.campaign_name),
        ("D0",          result.d0.strftime("%d/%m/%Y")),
        ("T (go-live)", result.t.strftime("%d/%m/%Y")),
        ("T-2",         d.milestone_t2),
        ("T-1",         d.milestone_t1),
    ]
    cells = "".join(
        f'<div style="display:flex; align-items:baseline; gap:8px; margin-bottom:5px;">'
        f'<span style="color:#6B7280; font-size:12px; min-width:90px; flex-shrink:0;">{k}</span>'
        f'<span style="color:#111827; font-size:13px; font-weight:500;">{v}</span>'
        f"</div>"
        for k, v in rows
    )
    return (
        '<div style="background:#F9FAFB; border:1px solid #E6E8EB; border-radius:10px; '
        "padding:16px 20px; margin-bottom:16px;\">"
        '<div style="font-size:12px; font-weight:600; color:#6B7280; '
        'text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;">'
        "Campaign Summary</div>"
        f"{cells}"
        "</div>"
    )


# ── Gantt renderer ─────────────────────────────────────────────────────────

def _aw(d, n: int):
    """add_working_days wrapper for UI — avoids importing at module level."""
    from src.draft_confirmation.date_utils import add_working_days  # noqa: PLC0415
    return add_working_days(d, n)


def _truncate_label(label: str, max_len: int = 60) -> tuple[str, str]:
    """Return (display_label, full_label_for_tooltip). Truncates at max_len."""
    if len(label) <= max_len:
        return label, ""
    return label[:max_len - 3] + "...", label


def render_uc4_gantt_html(result) -> str:
    """
    Build a clean bordered-bar HTML Gantt from a TimelineResult.

    Visual rules (Option 1)
    ───────────────────────
    • Standard rows (Biz / Design / Product Confirmation (PO)):
      One continuous colspan bar from D0 → due date.
      White bg, 2px colored border, due-marker dot at right.
    • Ops: ONE rowspan=3 actor cell + separate subtrack column per subrow:
        - clear       : bar from D0 → ops_due (green)
        - chưa-clear  : bar from max(biz_due,pc_due)+1wd → ops_due (blue)
        - UI          : bar from design_due+1wd → ops_due (green)
    • Milestone row at bottom.
    • Dependencies card below table.
    • No color legend.
    • Dark green header background.
    • Horizontal scroll; actor column sticky (rowspan cell sticky for Ops).
    """
    if result.errors:
        items = "".join(
            f'<p style="color:#DC2626; margin:4px 0; font-size:13px;">[ERROR] {e}</p>'
            for e in result.errors
        )
        return f'<div style="font-family:sans-serif; padding:12px;">{items}</div>'

    # ── Colors ────────────────────────────────────────────────────────────────
    BLUE      = "#0068FF"           # Biz / PC / Ops chưa-clear
    GREEN_BAR = "#00A64A"           # Design / Ops clear / Ops UI
    HDR_BG    = "#006B3F"           # dark green table header
    EMPTY_BG  = "#F9FAFB"

    # ── Data extraction ───────────────────────────────────────────────────────
    d0    = result.d0
    t     = result.t
    draft = result.draft

    by_role    = {tk.role: tk for tk in draft.tickets}
    biz_due    = _parse_dd_mm_yyyy(by_role["Biz"].due_date)                  if "Biz"                  in by_role else None
    design_due = _parse_dd_mm_yyyy(by_role["Design"].due_date)               if "Design"               in by_role else None
    pc_due     = _parse_dd_mm_yyyy(by_role["Product Confirmation"].due_date) if "Product Confirmation" in by_role else None
    ops_due    = _parse_dd_mm_yyyy(by_role["Ops"].due_date)                  if "Ops"                  in by_role else None

    # ── Ops dependency start dates ────────────────────────────────────────────
    ops_clear_start = d0
    if biz_due and pc_due:
        ops_chua_clear_start = _aw(max(biz_due, pc_due), 1)
    elif biz_due:
        ops_chua_clear_start = _aw(biz_due, 1)
    elif pc_due:
        ops_chua_clear_start = _aw(pc_due, 1)
    else:
        ops_chua_clear_start = ops_due  # no deps → use ops_due as fallback

    if design_due:
        ops_ui_start = _aw(design_due, 1)
    else:
        ops_ui_start = ops_due  # no design dep

    t2 = _parse_dd_mm_yyyy(draft.milestone_t2)
    t1 = _parse_dd_mm_yyyy(draft.milestone_t1)

    dates    = [d0 + timedelta(days=i) for i in range((t - d0).days + 1)]
    short_nm = _short_campaign_name(draft.campaign_name)

    n_dates = len(dates)

    # ── CSS helpers ───────────────────────────────────────────────────────────
    _EC = (
        f"background:{EMPTY_BG}; border:1px solid #E6E8EB; "
        "padding:4px 2px; font-size:11px;"
    )
    _TH = (
        f"background:{HDR_BG}; color:#FFFFFF; font-weight:600; font-size:11px; "
        "padding:6px 6px; border:1px solid #004F2D; text-align:center; white-space:nowrap;"
    )
    _WH = "background:white; border:1px solid #E6E8EB; padding:4px 2px; font-size:11px;"

    def _th_actor() -> str:
        return (
            _TH + " position:sticky; left:0; z-index:3; text-align:left; "
            "min-width:130px; max-width:130px;"
        )

    def _th_subtrack() -> str:
        return (
            _TH + " position:sticky; left:130px; z-index:3; text-align:left; "
            "min-width:85px; max-width:85px; border-left:1px solid #004F2D;"
        )

    def _td_actor(bg: str, fg: str = "#FFFFFF", rowspan: int = 1) -> str:
        rs = f' rowspan="{rowspan}"' if rowspan > 1 else ""
        return (
            f"background:{bg}; color:{fg}; font-weight:600; font-size:12px; "
            "border:1px solid #E6E8EB; "
            f"position:sticky; left:0; z-index:2; text-align:left; "
            f"min-width:130px; max-width:130px; padding:8px 10px; vertical-align:middle;"
            f'"{rs}>'
        )

    def _td_subtrack(label: str, bg: str = "#F0FDF4", fg: str = "#065F46") -> str:
        return (
            f'<td style="background:{bg}; color:{fg}; font-size:11px; font-weight:600; '
            f"border:1px solid #E6E8EB; "
            f"position:sticky; left:130px; z-index:1; "
            f"min-width:85px; max-width:85px; padding:5px 8px; vertical-align:middle; "
            f'white-space:nowrap;">{label}</td>'
        )

    def col_label(d) -> str:
        s = d.strftime("%d/%m")
        if d == d0:        return f"D0<br><small>{s}</small>"
        if d == t:         return f"T<br><small>{s}</small>"
        if t2 and d == t2: return f"T-2<br><small>{s}</small>"
        if t1 and d == t1: return f"T-1<br><small>{s}</small>"
        return s

    def _bar_cells_full(start, due, bar_color: str, label: str) -> str:
        """
        Emit colspan cells covering the entire date range [d0..t].
        Bar spans [start..due] with pre/post empty cells.
        start defaults to d0 if None.
        """
        eff_start = start if start is not None else d0
        # Clamp to visible range
        eff_start = max(eff_start, d0)

        if due is None:
            return (
                f'<td colspan="{n_dates}" style="{_EC} '
                f'color:#9CA3AF; font-style:italic; text-align:center;">'
                f"không phát sinh</td>"
            )

        eff_due = min(due, t)

        if eff_start > eff_due:
            # Bar entirely outside range — show info
            return (
                f'<td colspan="{n_dates}" style="{_EC} '
                f'color:#F59E0B; font-style:italic; text-align:center;">'
                f"start sau ngày kết thúc bảng</td>"
            )

        n_pre  = (eff_start - d0).days
        n_bar  = (eff_due - eff_start).days + 1
        n_post = (t - eff_due).days

        display_lbl, tooltip = _truncate_label(label)
        title_attr = f' title="{tooltip}"' if tooltip else ""

        dot = (
            f'<span style="display:inline-block; width:8px; height:8px; '
            f'background:{bar_color}; border-radius:50%; '
            f'flex-shrink:0; margin-left:4px;"></span>'
        )
        inner = (
            f'<div style="display:flex; align-items:center; '
            f'justify-content:space-between; gap:4px; min-height:28px;">'
            f'<span style="font-size:11px; color:#1F2937; line-height:1.4; '
            f'word-break:break-word; white-space:normal; overflow:hidden; '
            f'display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical;">'
            f"{display_lbl}</span>"
            f"{dot}</div>"
        )
        bar_td = (
            f'<td colspan="{n_bar}" '
            f'style="background:white; border:2px solid {bar_color}; border-radius:4px; '
            f'padding:4px 8px; vertical-align:middle; min-width:{n_bar * 38}px;"'
            f"{title_attr}>{inner}</td>"
        )

        cells: list[str] = []
        if n_pre > 0:
            cells.append(f'<td colspan="{n_pre}" style="{_EC}"></td>')
        cells.append(bar_td)
        if n_post > 0:
            cells.append(f'<td colspan="{n_post}" style="{_EC}"></td>')
        return "".join(cells)

    # ── Assemble table ────────────────────────────────────────────────────────
    h: list[str] = []
    h.append(
        '<div style="overflow-x:auto; width:100%; font-family:sans-serif; '
        'background:#FFFFFF; border:1px solid #E6E8EB; border-radius:10px; padding:12px;">'
    )
    h.append('<table style="border-collapse:collapse; background:#FFFFFF; width:max-content;">')

    # ── Header row ────────────────────────────────────────────────────────────
    h.append("<thead><tr>")
    h.append(f'<th style="{_th_actor()}">Actor</th>')
    h.append(f'<th style="{_th_subtrack()}">Track</th>')
    for d in dates:
        h.append(f'<th style="{_TH}">{col_label(d)}</th>')
    h.append("</tr></thead><tbody>")

    # ── Standard rows (Biz / Design / Product Confirmation (PO)) ─────────────
    std_rows = [
        ("Biz",                       biz_due,    BLUE,      f"{short_nm} — clear requirement"),
        ("Design",                     design_due, GREEN_BAR, f"{short_nm} — design UI"),
        ("Product Confirmation (PO)",  pc_due,     BLUE,      f"{short_nm} — review and confirm request"),
    ]
    for display_role, due, clr, label in std_rows:
        h.append("<tr>")
        # Actor cell
        h.append(
            f'<td style="background:{clr}; color:#FFFFFF; font-weight:600; font-size:12px; '
            f"border:1px solid #E6E8EB; position:sticky; left:0; z-index:2; "
            f'min-width:130px; max-width:130px; padding:8px 10px; vertical-align:middle;">'
            f"{display_role}</td>"
        )
        # Subtrack cell (empty for standard rows)
        h.append(
            f'<td style="background:#F9FAFB; border:1px solid #E6E8EB; '
            f"position:sticky; left:130px; z-index:1; "
            f'min-width:85px; max-width:85px; padding:5px 8px;"></td>'
        )
        h.append(_bar_cells_full(d0, due, clr, label))
        h.append("</tr>")

    # ── Ops group — 3 subrows, actor cell spans all 3 ────────────────────────
    if ops_due is None:
        # No Ops ticket — single row with info message
        h.append("<tr>")
        h.append(
            f'<td style="background:{GREEN_BAR}; color:#FFFFFF; font-weight:600; '
            f"font-size:12px; border:1px solid #E6E8EB; position:sticky; left:0; z-index:2; "
            f'min-width:130px; max-width:130px; padding:8px 10px; vertical-align:middle;">'
            f"Ops</td>"
        )
        h.append(
            f'<td colspan="{n_dates + 1}" style="{_EC} '
            f'color:#9CA3AF; font-style:italic; text-align:center;">không phát sinh</td>'
        )
        h.append("</tr>")
    else:
        ops_subtracks = [
            ("clear",       ops_clear_start,       ops_due, GREEN_BAR,
             f"{short_nm} — setup những thứ đã clear"),
            ("chưa-clear",  ops_chua_clear_start,  ops_due, BLUE,
             f"{short_nm} — setup những thứ chưa clear"),
            ("UI",          ops_ui_start,           ops_due, GREEN_BAR,
             f"{short_nm} — setup UI"),
        ]
        for i, (track_label, t_start, t_end, t_color, t_bar_label) in enumerate(ops_subtracks):
            h.append("<tr>")

            # Actor cell: only on first subrow, rowspan=3
            if i == 0:
                h.append(
                    f'<td rowspan="3" style="background:{GREEN_BAR}; color:#FFFFFF; '
                    f"font-weight:600; font-size:12px; border:1px solid #E6E8EB; "
                    f"position:sticky; left:0; z-index:2; "
                    f"min-width:130px; max-width:130px; padding:8px 10px; "
                    f'vertical-align:middle; text-align:center;">Ops</td>'
                )

            # Subtrack label cell
            h.append(_td_subtrack(track_label))

            # Bar cells
            h.append(_bar_cells_full(t_start, t_end, t_color, t_bar_label))
            h.append("</tr>")

    # ── Milestone row ─────────────────────────────────────────────────────────
    ms_map: dict = {}
    if t2: ms_map[t2] = ("T-2: gửi link test",  "#EAF2FF", "#1E40AF", "normal")
    if t1: ms_map[t1] = ("T-1: update feedback", "#EAF2FF", "#1E40AF", "normal")
    ms_map[t] = ("GO LIVE", "#EAF8EF", "#065F46", "bold")

    h.append("<tr>")
    h.append(
        '<td style="background:#F9FAFB; color:#6B7280; font-style:italic; font-size:11px; '
        "border:1px solid #E6E8EB; position:sticky; left:0; z-index:2; "
        'min-width:130px; max-width:130px; padding:8px 10px; vertical-align:middle;">Milestones</td>'
    )
    # Empty subtrack cell for milestones row
    h.append('<td style="background:#F9FAFB; border:1px solid #E6E8EB; min-width:85px;"></td>')
    for d in dates:
        entry = ms_map.get(d)
        if entry:
            lbl, bg, fg, fw = entry
            h.append(
                f'<td style="background:{bg}; color:{fg}; font-weight:{fw}; '
                f"border:1px solid #E6E8EB; font-size:11px; padding:4px 6px; "
                f'text-align:center; white-space:nowrap;">{lbl}</td>'
            )
        else:
            h.append(f'<td style="{_WH} background:white;"></td>')
    h.append("</tr>")

    h.append("</tbody></table></div>")

    # ── Dependencies card ─────────────────────────────────────────────────────
    dep_warnings: list[str] = []

    # Check for out-of-range dependency starts
    if ops_due:
        if ops_chua_clear_start and ops_chua_clear_start > ops_due:
            dep_warnings.append(
                f"Ops chưa-clear start ({ops_chua_clear_start.strftime('%d/%m/%Y')}) "
                f"is after Ops due ({ops_due.strftime('%d/%m/%Y')}) — check SLA."
            )
        if ops_ui_start and ops_ui_start > ops_due:
            dep_warnings.append(
                f"Ops UI start ({ops_ui_start.strftime('%d/%m/%Y')}) "
                f"is after Ops due ({ops_due.strftime('%d/%m/%Y')}) — check SLA."
            )

    dep: list[str] = []
    dep.append(
        f"Ops clear: starts D0 ({d0.strftime('%d/%m/%Y')}), due {ops_due.strftime('%d/%m/%Y') if ops_due else 'N/A'}"
    )
    if biz_due and pc_due:
        dep.append(
            f"Ops chưa-clear: starts after max(Biz due {biz_due.strftime('%d/%m/%Y')}, "
            f"PC due {pc_due.strftime('%d/%m/%Y')}) + 1 working day "
            f"= {ops_chua_clear_start.strftime('%d/%m/%Y')}"
        )
    if design_due:
        dep.append(
            f"Ops UI: starts after Design due ({design_due.strftime('%d/%m/%Y')}) "
            f"+ 1 working day = {ops_ui_start.strftime('%d/%m/%Y')}"
        )
    dep.append(
        f"Milestones: T-2 = {draft.milestone_t2} (gửi link test)"
        f" | T-1 = {draft.milestone_t1} (update feedback)"
        f" | T = {t.strftime('%d/%m/%Y')} (GO LIVE)"
    )
    if draft.guardrail_alert:
        dep.append(f"GUARDRAIL: {draft.guardrail_alert}")
    dep.extend(dep_warnings)

    def _dep_li(text: str, warn: bool = False) -> str:
        bullet_clr = "#F59E0B" if warn else "#00A64A"
        return (
            f'<li style="list-style:none; margin:5px 0; display:flex; gap:8px;">'
            f'<span style="color:{bullet_clr}; font-weight:700; flex-shrink:0;">•</span>'
            f'<span style="color:#374151; font-size:13px;">{text}</span></li>'
        )

    dep_items_html = "".join(_dep_li(item, warn=(item in dep_warnings)) for item in dep)

    h.append(
        '<div style="margin-top:16px; background:#FFFFFF; border:1px solid #E6E8EB; '
        "border-radius:10px; padding:16px 20px;\">"
        '<div style="font-size:14px; font-weight:600; color:#111827; margin-bottom:8px;">'
        "Dependencies &amp; Timeline"
        "</div>"
        f'<ul style="margin:0; padding:0;">{dep_items_html}</ul>'
        "</div>"
    )

    return "".join(h)


# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Product Ops Campaign Agent",
    layout="wide",
)

inject_app_css()

st.title("Product Ops Campaign Agent — Local Demo")

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "UC1 · Review Campaign Request",
    "UC2 · Setup Guide Q&A",
    "UC3 · Generate Ticket Content",
    "UC4 · Timeline Campaign Assistant",
])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — UC1: Review Campaign Request
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("UC1 · Review Campaign Request")
    st.markdown(
        "<p style='color:#6B7280; font-size:14px; margin-top:-8px; margin-bottom:16px;'>"
        "Select a campaign request file. The agent checks Game Type, Task Triggers, "
        "and Reward Types against the local KB allowlist and splits the result into "
        "<strong>supported</strong> and <strong>needs confirmation</strong>."
        "</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    samples = _list_samples()
    if not samples:
        st.error("No sample files found in data/samples/. Check your repository structure.")
    else:
        col_sel, col_btn, col_st = st.columns([5, 2, 2])
        with col_sel:
            selected_name_uc1 = st.selectbox(
                "Campaign request file", [p.name for p in samples], key="uc1_file"
            )
        with col_btn:
            # Spacer matching selectbox label height
            st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
            run_uc1 = st.button(
                "Run Review", key="uc1_run", type="primary", use_container_width=True
            )

        if run_uc1:
            selected_path_uc1 = str(_SAMPLES_DIR / selected_name_uc1)
            with col_st:
                st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
                st.markdown(render_status_box("Review completed."), unsafe_allow_html=True)
            try:
                output = run_review_for_ui(selected_path_uc1)
                st.code(output, language=None)
            except FileNotFoundError as exc:
                st.error(f"File not found: {exc}")
            except ValueError as exc:
                st.error(f"Cannot parse request — {exc}")
            except Exception as exc:
                st.error(f"Unexpected error — {type(exc).__name__}: {exc}")
                with st.expander("Debug details"):
                    st.code(traceback.format_exc(), language=None)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — UC2: Setup Guide Q&A
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("UC2 · Setup Guide Q&A")
    st.markdown(
        "<p style='color:#6B7280; font-size:14px; margin-top:-8px; margin-bottom:16px;'>"
        "Ask a natural-language question about campaign tool setup. "
        "The agent searches the local KB and returns the relevant steps plus "
        "the exact source section."
        "</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    question = st.text_input(
        "Your question",
        placeholder='"cách setup Game Type lucky wheel"',
        key="uc2_question",
    )
    st.caption(
        'Examples: "cách setup Game Type lucky wheel"'
        ' · "cách setup task trigger payment"'
        ' · "tạo reward pool"'
        ' · "setup leaderboard"'
    )

    if st.button("Ask", key="uc2_ask", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                answer = run_ask_for_ui(question.strip())
                st.markdown(render_status_box("Answer found."), unsafe_allow_html=True)
                st.code(answer, language=None)
            except FileNotFoundError as exc:
                st.error(f"KB file not found: {exc}")
            except Exception as exc:
                st.error(f"Unexpected error — {type(exc).__name__}: {exc}")
                with st.expander("Debug details"):
                    st.code(traceback.format_exc(), language=None)

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — UC3: Generate Ticket Content
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("UC3 · Generate Ticket Content")
    st.markdown(
        "<p style='color:#6B7280; font-size:14px; margin-top:-8px; margin-bottom:16px;'>"
        "Select a campaign request file. The agent runs UC1 review internally, "
        "then drafts up to <strong>4 coordination tickets</strong> "
        "(Biz / Design / Product Confirmation / Ops) with SLAs and dependencies."
        "</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    samples_uc3 = _list_samples()
    if not samples_uc3:
        st.error("No sample files found in data/samples/.")
    else:
        col_sel3, col_btn3, col_st3 = st.columns([5, 2, 2])
        with col_sel3:
            selected_name_uc3 = st.selectbox(
                "Campaign request file", [p.name for p in samples_uc3], key="uc3_file"
            )
        with col_btn3:
            st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
            run_uc3 = st.button(
                "Generate Tickets", key="uc3_run", type="primary", use_container_width=True
            )

        if run_uc3:
            selected_path_uc3 = str(_SAMPLES_DIR / selected_name_uc3)
            with col_st3:
                st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
                st.markdown(
                    render_status_box("Ticket content generated."), unsafe_allow_html=True
                )
            try:
                _, output = run_ticket_generation_for_ui(selected_path_uc3)
                st.subheader("Ticket content — copy-paste to Jira")
                st.markdown(
                    render_info_card(
                        "Review each ticket below. Fill in real names at "
                        "<strong>[assignee]</strong> before copying to Jira. "
                        "The agent drafts only — no automatic Jira writes."
                    ),
                    unsafe_allow_html=True,
                )
                st.code(output, language=None)
                st.download_button(
                    label="Download as .txt",
                    data=output.encode("utf-8"),
                    file_name=f"ticket_draft_{selected_name_uc3.replace('.md', '')}.txt",
                    mime="text/plain",
                    key="uc3_download",
                )
                st.caption(
                    "Điền tên người/nhóm thật "
                    "vào chỗ [assignee] trước khi gửi."
                )
            except FileNotFoundError as exc:
                st.error(f"File not found: {exc}")
            except ValueError as exc:
                st.error(f"Cannot parse request — {exc}")
            except Exception as exc:
                st.error(
                    f"Unexpected error — please check the request file format. "
                    f"{type(exc).__name__}: {exc}"
                )
                with st.expander("Debug details"):
                    st.code(traceback.format_exc(), language=None)

# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — UC4: Timeline Campaign Assistant
# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("UC4 · Timeline Campaign Assistant")
    st.markdown(
        "<p style='color:#6B7280; font-size:14px; margin-top:-8px; margin-bottom:16px;'>"
        "Select a campaign request file. The agent runs UC3 internally, "
        "then generates a Gantt-style timeline with fixed actor rows and "
        "one column per calendar date from D0 to go-live."
        "</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    samples_uc4 = _list_samples()
    if not samples_uc4:
        st.error("No sample files found in data/samples/.")
    else:
        col_sel4, col_btn4, col_st4 = st.columns([5, 2, 2])
        with col_sel4:
            selected_name_uc4 = st.selectbox(
                "Campaign request file", [p.name for p in samples_uc4], key="uc4_file"
            )
        with col_btn4:
            st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
            run_uc4 = st.button(
                "Generate Timeline", key="uc4_run", type="primary", use_container_width=True
            )

        if run_uc4:
            selected_path_uc4 = str(_SAMPLES_DIR / selected_name_uc4)
            try:
                result     = get_timeline_result_for_ui(selected_path_uc4)
                txt_output = result.render()   # unchanged ASCII — for download only

                with col_st4:
                    st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
                    st.markdown(
                        render_status_box("Timeline generated successfully."),
                        unsafe_allow_html=True,
                    )

                # Summary card
                st.markdown(render_uc4_summary_card(result), unsafe_allow_html=True)

                # Gantt
                st.markdown(render_uc4_gantt_html(result), unsafe_allow_html=True)

                # Tips card
                st.markdown(
                    render_info_card(
                        "Review the timeline before use. If anything needs adjustment, "
                        "update the request or UC3 output first, then generate again."
                    ),
                    unsafe_allow_html=True,
                )
                st.write("")

                # Download
                st.download_button(
                    label="Download as .txt",
                    data=txt_output.encode("utf-8"),
                    file_name=f"timeline_{selected_name_uc4.replace('.md', '')}.txt",
                    mime="text/plain",
                    key="uc4_download",
                )

            except FileNotFoundError as exc:
                st.error(f"File not found: {exc}")
            except ValueError as exc:
                st.error(f"Cannot parse request — {exc}")
            except Exception as exc:
                st.error(
                    f"Unexpected error — please check the request file format. "
                    f"{type(exc).__name__}: {exc}"
                )
                with st.expander("Debug details"):
                    st.code(traceback.format_exc(), language=None)
