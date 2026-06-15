"""
Timeline Campaign Assistant (UC4) — Gantt-style markdown grid.

Reads a campaign request file, internally calls generate_draft() (UC3),
and renders a date-column timeline grid with fixed 4 actor rows.

Rules:
- No external API calls. Local files only.
- Single input contract: filepath to campaign request .md
- Always renders all 4 rows: Biz, Design, Product Confirmation, Ops
- Ops has 3 internal tracks; only 'clear' starts at D0
- Columns = one per calendar date from D0 through T; no week grouping
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from src.draft_confirmation.generator import DraftResult, generate_draft
from src.draft_confirmation.date_utils import fmt, subtract_working_days


def _parse_fmt_date(s: str) -> date | None:
    """Parse dd/mm/yyyy → date; return None on failure."""
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def _col_header(d: date, d0: date, t: date, t2: date, t1: date) -> str:
    day_str = d.strftime("%d/%m")
    if d == d0:
        return f"D0 {day_str}"
    if d == t:
        return f"T {day_str}"
    if d == t2:
        return f"T-2 {day_str}"
    if d == t1:
        return f"T-1 {day_str}"
    return day_str


def _actor_cell(d: date, d0: date, due: date, brief: str) -> str:
    """Render one cell for a simple (non-Ops) actor row."""
    if d == d0:
        return f"▓ {brief}"
    if d0 < d < due:
        return "→"
    if d == due:
        return "✓"
    return ""


def _ops_cell(
    d: date,
    d0: date,
    ops_due: date,
    has_unclear: bool,
    pc_due: date | None,
    pc_due_str: str,
    has_ui: bool,
    design_due: date | None,
    design_due_str: str,
) -> str:
    """Render one cell for the Ops row — 3 sub-tracks joined by <br>."""
    parts: list[str] = []

    # Track 1: clear — starts at D0, runs to ops_due
    if d == d0:
        parts.append("▓ clear: config items")
    elif d0 < d < ops_due:
        parts.append("→ clear")
    elif d == ops_due:
        parts.append("✓ clear")
    else:
        parts.append("")

    # Track 2: chưa-clear — waits for Product Confirmation
    if not has_unclear:
        parts.append("· không phát sinh")
    elif d < pc_due:
        parts.append(f"· chờ PC (due {pc_due_str})")
    elif d == pc_due:
        parts.append("▓ chưa-clear: start")
    elif pc_due < d < ops_due:
        parts.append("→ chưa-clear")
    elif d == ops_due:
        parts.append("✓ chưa-clear")
    else:
        parts.append("")

    # Track 3: UI — waits for Design
    if not has_ui:
        parts.append("· không phát sinh")
    elif d < design_due:
        parts.append(f"· chờ Design (due {design_due_str})")
    elif d == design_due:
        parts.append("▓ UI: start config")
    elif design_due < d < ops_due:
        parts.append("→ UI")
    elif d == ops_due:
        parts.append("✓ UI")
    else:
        parts.append("")

    joined = "<br>".join(parts)
    # If all tracks are empty (past ops_due), return blank cell
    return "" if joined.replace("<br>", "").strip() == "" else joined


def _make_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _make_sep(n: int) -> str:
    return "|" + "|".join(["---"] * n) + "|"


def _render_grid(r: "TimelineResult") -> str:
    draft = r.draft
    d0 = r.d0
    t = r.t

    t2 = subtract_working_days(t, 2)
    t1 = subtract_working_days(t, 1)

    # All calendar dates D0 .. T (inclusive)
    num_days = (t - d0).days + 1
    dates: list[date] = [d0 + timedelta(days=i) for i in range(num_days)]

    # Locate tickets by role
    biz_tk = next((tk for tk in draft.tickets if tk.role == "Biz"), None)
    design_tk = next((tk for tk in draft.tickets if tk.role == "Design"), None)
    pc_tk = next((tk for tk in draft.tickets if tk.role == "Product Confirmation"), None)
    ops_tk = next((tk for tk in draft.tickets if tk.role == "Ops"), None)

    # Parse due dates
    biz_due = _parse_fmt_date(biz_tk.due_date) if biz_tk else None
    design_due = _parse_fmt_date(design_tk.due_date) if design_tk else None
    pc_due = _parse_fmt_date(pc_tk.due_date) if pc_tk else None
    ops_due = _parse_fmt_date(ops_tk.due_date) if ops_tk else None

    has_unclear = pc_tk is not None
    has_ui = design_tk is not None
    pc_due_str = pc_tk.due_date if pc_tk else ""
    design_due_str = design_tk.due_date if design_tk else ""

    # ── Header ────────────────────────────────────────────────────────────────
    header_cells = ["Actor / PIC"] + [_col_header(d, d0, t, t2, t1) for d in dates]
    sep = _make_sep(len(header_cells))

    # ── Biz row ───────────────────────────────────────────────────────────────
    if biz_tk is None or biz_due is None:
        biz_cells = ["Biz", "không phát sinh"] + [""] * (len(dates) - 1)
    else:
        biz_cells = ["Biz"] + [_actor_cell(d, d0, biz_due, "input fields") for d in dates]

    # ── Design row ────────────────────────────────────────────────────────────
    if design_tk is None or design_due is None:
        design_cells = ["Design", "không phát sinh"] + [""] * (len(dates) - 1)
    else:
        design_cells = ["Design"] + [_actor_cell(d, d0, design_due, "thiết kế UI") for d in dates]

    # ── Product Confirmation row ──────────────────────────────────────────────
    if pc_tk is None or pc_due is None:
        pc_cells = ["Product Confirmation", "không phát sinh"] + [""] * (len(dates) - 1)
    else:
        pc_cells = ["Product Confirmation"] + [_actor_cell(d, d0, pc_due, "confirm items") for d in dates]

    # ── Ops row ───────────────────────────────────────────────────────────────
    # Ops ticket is always generated — ops_due should never be None
    if ops_tk is None or ops_due is None:
        ops_cells = ["Ops", "không phát sinh"] + [""] * (len(dates) - 1)
    else:
        ops_cells = ["Ops"] + [
            _ops_cell(d, d0, ops_due, has_unclear, pc_due, pc_due_str, has_ui, design_due, design_due_str)
            for d in dates
        ]

    # ── Milestones row ────────────────────────────────────────────────────────
    milestone_cells: list[str] = ["— Milestones —"]
    for d in dates:
        if d == t2:
            milestone_cells.append("gửi link test")
        elif d == t1:
            milestone_cells.append("update feedback")
        elif d == t:
            milestone_cells.append("GO LIVE")
        else:
            milestone_cells.append("")

    # ── Assemble ──────────────────────────────────────────────────────────────
    lines: list[str] = [
        f"=== TIMELINE: {draft.campaign_name} ===",
        f"D0: {fmt(d0)} | T (go-live): {fmt(t)}",
        f"Milestones: T-2 = {fmt(t2)} (gửi link test) | T-1 = {fmt(t1)} (update) | T = {fmt(t)} (GO LIVE)",
        "",
        _make_row(header_cells),
        sep,
        _make_row(biz_cells),
        _make_row(design_cells),
        _make_row(pc_cells),
        _make_row(ops_cells),
        _make_row(milestone_cells),
        "",
        "📌 Dependencies:",
    ]
    if has_unclear and pc_due:
        lines.append(f"• Ops–chưa-clear: starts after Product Confirmation ticket due ({pc_due_str})")
    if has_ui and design_due:
        lines.append(f"• Ops–UI: starts after Design ticket due ({design_due_str})")
    lines.append(f"• Milestones: T-2 = {fmt(t2)} gửi link test | T-1 = {fmt(t1)} update | T = {fmt(t)} GO LIVE")
    lines.append("")
    lines.append("⚠️ Ops: review timeline below. Nếu cần chỉnh sửa, chạy lại UC3 trước khi dùng.")

    # Propagate any UC3-level guardrail
    if draft.guardrail_alert:
        lines.append(f"⚠️ GUARDRAIL: {draft.guardrail_alert}")

    return "\n".join(lines)


# ── Public dataclass ──────────────────────────────────────────────────────────

@dataclass
class TimelineResult:
    campaign_name: str
    d0: date
    t: date
    draft: DraftResult
    errors: list[str] = field(default_factory=list)

    def render(self) -> str:
        if self.errors:
            header = f"=== TIMELINE: {self.campaign_name} ==="
            error_lines = [f"[ERROR] {e}" for e in self.errors]
            return "\n".join([header, ""] + error_lines)
        return _render_grid(self)


# ── Entry point ───────────────────────────────────────────────────────────────

def generate_timeline(filepath: str) -> TimelineResult:
    """
    Generate a Gantt-style markdown timeline from a campaign request file.

    Internally calls generate_draft() (UC3) then renders the timeline grid.
    Returns TimelineResult; call .render() for the text output.
    Raises FileNotFoundError if the request file is missing.
    """
    draft = generate_draft(filepath)

    d0 = datetime.strptime(draft.d0, "%d/%m/%Y").date()

    if draft.go_live_date == "(chưa có)":
        return TimelineResult(
            campaign_name=draft.campaign_name,
            d0=d0,
            t=d0,
            draft=draft,
            errors=["Thiếu ngày go-live — không dựng bảng timeline."],
        )

    try:
        t = datetime.strptime(draft.go_live_date, "%d/%m/%Y").date()
    except ValueError:
        return TimelineResult(
            campaign_name=draft.campaign_name,
            d0=d0,
            t=d0,
            draft=draft,
            errors=[f"Không đọc được ngày go-live '{draft.go_live_date}'."],
        )

    return TimelineResult(
        campaign_name=draft.campaign_name,
        d0=d0,
        t=t,
        draft=draft,
        errors=list(draft.errors),
    )
