"""
Draft Confirmation Generator (UC3) — Ticket & Stakeholder Coordinator.

Reads a campaign request file, runs UC1 review internally, and drafts
content for up to 4 tickets (Biz / Design / PO / Ops).

Rules (per spec UC3 v1.3):
- No external API calls. Local files only.
- Agent does NOT write to Jira — only exports text for Ops to copy.
- Ticket generation conditions:
    Biz    → required template field missing or missing description
    Design → "Game UI" section present in request
    PO     → any UC1 needs-confirm items exist
    Ops    → always generated; 3 parts (clear / pending-PO / pending-Design)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from src.draft_confirmation.date_utils import (
    add_working_days,
    subtract_working_days,
    fmt,
)
from src.review.parser import parse_request
from src.review.reviewer import review_request, ReviewResult
from src.setup_guide.rag import answer_question

# ── Template required fields (UC3 §5 — fields marked * in template) ──────────
REQUIRED_FIELDS: list[str] = [
    "campaign name",
    "game type",
    "marketing code",
    "thời gian diễn ra",   # go-live date T
    "start date",
    "end date",
    "tnc link",
    "mô tả chương trình",  # program description — commonly missing
]

# Human-readable display labels for each required field
_FIELD_LABELS: dict[str, str] = {
    "campaign name":        "Campaign Name",
    "game type":            "Game Type",
    "marketing code":       "Marketing Code",
    "thời gian diễn ra":    "Thời gian diễn ra (go-live)",
    "start date":           "Start Date",
    "end date":             "End Date",
    "tnc link":             "TnC Link",
    "mô tả chương trình":   "Mô tả chương trình",
}


def _strip_md(s: str) -> str:
    """Remove markdown bold/italic markers (**) from a string."""
    return s.replace("**", "").replace("__", "").strip()


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Ticket:
    role: str          # Biz / Design / PO / Ops
    assignee: str      # same as role (placeholder for Ops to fill)
    condition: str     # campaign name this ticket is for
    context: str
    request_body: str
    related_doc: str
    sla: str
    due_date: str
    dependency: str = ""
    brief: bool = False  # if True, render only Context + Request (Ops ticket)

    def render(self) -> str:
        lines = [
            f"--- TICKET: {self.role.upper()} ---",
            f"Dear {self.assignee},",
            f"Để support cho campaign [{self.condition}],",
            f"nhờ bạn support giúp:",
            "",
            f"• Context:      {self.context}",
            f"• Request:\n{self.request_body}",
        ]
        if not self.brief:
            lines.append(f"• Related doc:  {self.related_doc}")
            lines.append(f"• Timeline:     SLA {self.sla} — due {self.due_date}")
            if self.dependency:
                lines.append(f"• Dependency:   {self.dependency}")
        return "\n".join(lines)


@dataclass
class DraftResult:
    campaign_name: str
    go_live_date: str
    d0: str
    milestone_t2: str
    milestone_t1: str
    guardrail_alert: str
    tickets: list[Ticket] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def render(self) -> str:
        """Returns ticket content only — starts directly with first ticket block."""
        lines = []
        if self.guardrail_alert:
            lines.append(f"GUARDRAIL: {self.guardrail_alert}")
            lines.append("")
        if self.errors:
            for e in self.errors:
                lines.append(f"[ERROR] {e}")
            return "\n".join(lines)
        for ticket in self.tickets:
            lines.append(ticket.render())
            lines.append("")
        while lines and lines[-1] == "":
            lines.pop()
        return "\n".join(lines)

    def render_metadata(self) -> str:
        """Returns campaign metadata header — for display, not for Jira copy-paste."""
        lines = [
            f"=== DRAFT CONFIRMATION TICKETS: {self.campaign_name} ===",
            f"Generated: {self.d0} | T (go-live): {self.go_live_date}",
            (
                f"Milestones: T-2 = {self.milestone_t2} (gửi link test)"
                f" | T-1 = {self.milestone_t1} (update theo feedback)"
                f" | T = {self.go_live_date} (go live)"
            ),
            (
                "Ops phai review noi dung ben duoi truoc khi copy-paste sang Jira. "
                "Agent chi soan nhap — KHONG ghi Jira tu dong."
            ),
        ]
        if self.guardrail_alert:
            lines.append(f"\nGUARDRAIL: {self.guardrail_alert}")
        return "\n".join(lines)


# ── Main generator ────────────────────────────────────────────────────────────

def generate_draft(filepath: str) -> DraftResult:
    """
    Generate draft confirmation tickets from a campaign request file.

    Returns a DraftResult (call .render() for the text output).
    Raises FileNotFoundError if the request file is missing.
    """
    # ── Parse request ─────────────────────────────────────────────────────────
    request = parse_request(filepath)
    campaign_name = request["campaign_name"]
    game_type = request["game_type"]
    general_fields: dict[str, str] = request.get("general_fields", {})
    game_ui: dict[str, str] = request.get("game_ui", {})
    go_live_str = request.get("go_live_date", "").strip()

    # Short display name for the input file (relative if inside cwd)
    try:
        rel_path = Path(filepath).resolve().relative_to(Path.cwd())
        input_file_ref = str(rel_path)
    except ValueError:
        input_file_ref = filepath

    d0: date = datetime.today().date()
    errors: list[str] = []

    # ── Resolve T (go-live date) ──────────────────────────────────────────────
    if not go_live_str:
        return DraftResult(
            campaign_name=campaign_name,
            go_live_date="(chua co)",
            d0=fmt(d0),
            milestone_t2="N/A",
            milestone_t1="N/A",
            guardrail_alert="",
            errors=[
                "Thieu ngay go-live (Thoi gian dien ra) trong request. "
                "Day la thieu thong tin request — Ops can them thong tin go-live, "
                "sau do chay lai lenh nay."
            ],
        )

    try:
        t: date = datetime.strptime(go_live_str, "%Y-%m-%d").date()
    except ValueError:
        return DraftResult(
            campaign_name=campaign_name,
            go_live_date=go_live_str,
            d0=fmt(d0),
            milestone_t2="N/A",
            milestone_t1="N/A",
            guardrail_alert="",
            errors=[
                f"Khong doc duoc ngay go-live '{go_live_str}'. "
                "Can format YYYY-MM-DD."
            ],
        )

    # ── Timeline milestones ───────────────────────────────────────────────────
    t_minus_2: date = subtract_working_days(t, 2)
    t_minus_1: date = subtract_working_days(t, 1)

    # ── Due dates per SLA (all working days) ──────────────────────────────────
    due_biz: date    = add_working_days(d0, 1)
    due_po: date     = add_working_days(d0, 1)
    due_design: date = add_working_days(d0, 5)
    due_ops: date    = add_working_days(d0, 10)

    # ── Guardrail: (T − D0) < 14 calendar days ───────────────────────────────
    delta_days = (t - d0).days
    guardrail = ""
    if delta_days < 14:
        guardrail = (
            f"(T - D0) = {delta_days} ngay < 2 tuan. "
            "Timeline ngan — Ops can dieu chinh lich; "
            "timeline xuat ben duoi giu nguyen de tham khao."
        )

    # ── UC1: run review internally ────────────────────────────────────────────
    uc1: ReviewResult = review_request(filepath)
    unclear_items = list(uc1.needs_confirm)
    clear_items   = list(uc1.supported)

    # ── UC2: setup guide lookup for game type ────────────────────────────────
    setup_guide_answer = answer_question(f"cach setup {game_type}")
    if "khong tim thay" in _strip_md(setup_guide_answer).lower():
        setup_guide_ref = "Khong co huong dan trong KB noi bo — hoi PO."
    else:
        nguon_line = next(
            (ln for ln in setup_guide_answer.splitlines() if "Ngu" in ln and "n" in ln),
            setup_guide_answer.split("\n")[0],
        )
        setup_guide_ref = _strip_md(nguon_line)

    # ── Build tickets ─────────────────────────────────────────────────────────
    tickets: list[Ticket] = []

    # ── TICKET 1: BIZ ────────────────────────────────────────────────────────
    # Detect each missing/incomplete field with a specific reason
    missing_field_details: list[tuple[str, str]] = []
    for f in REQUIRED_FIELDS:
        label = _FIELD_LABELS.get(f, f.title())
        if f not in general_fields:
            missing_field_details.append((label, "chua co trong request"))
        elif not general_fields[f].strip():
            missing_field_details.append((label, "chua co noi dung"))

    if missing_field_details:
        biz_req_lines = [
            "Nho ban bo sung/cap nhat cac field con thieu hoac thieu mo ta trong request:"
        ]
        for label, reason in missing_field_details:
            biz_req_lines.append(f"  - {label}: {reason}")
        tickets.append(Ticket(
            role="Biz",
            assignee="Biz",
            condition=campaign_name,
            context=(
                f"Campaign '{campaign_name}' (Game Type: {game_type}) "
                "dang trong giai doan chuan bi. "
                "Mot so field trong request con thieu hoac thieu mo ta."
            ),
            request_body="\n".join(biz_req_lines),
            related_doc=f"File request dau vao cua UC1: {input_file_ref}",
            sla="1 working day",
            due_date=fmt(due_biz),
        ))

    # ── TICKET 2: DESIGN ─────────────────────────────────────────────────────
    if game_ui:
        ui_lines = ["Nho ban thiet ke UI theo Game UI brief duoi day:"]
        for k, v in game_ui.items():
            ui_lines.append(f"  - {k}: {v}")
        tickets.append(Ticket(
            role="Design",
            assignee="Design",
            condition=campaign_name,
            context=(
                f"Campaign '{campaign_name}' dung Game Type: {game_type}. "
                "Request da co phan Game UI can thiet ke."
            ),
            request_body="\n".join(ui_lines),
            related_doc=(
                f"File request dau vao cua UC1: {input_file_ref}; "
                f"KB setup guide: {setup_guide_ref}"
            ),
            sla="5 working days",
            due_date=fmt(due_design),
        ))

    # ── TICKET 3: PRODUCT CONFIRMATION ───────────────────────────────────────
    if unclear_items:
        pc_lines = ["Nho Product Team confirm cac hang muc sau:"]
        for i, p in enumerate(unclear_items, start=1):
            # Determine item type label
            if p.category == "TASK":
                type_label = "Task"
            elif p.category == "REWARD":
                type_label = "Reward"
            else:
                type_label = p.category

            # Extract a short item name from the label
            item_name = (
                p.label
                .replace('Task "', "").replace('"', "")
                .replace("Reward ", "").strip()
            )
            pc_lines.append(f"\n{i}. {type_label}: {item_name}")
            pc_lines.append(f"   - Noi dung request: {p.content}")
            pc_lines.append(f"   - Ly do can confirm: {p.detail}")
            if p.po_question:
                pc_lines.append(f"   - Can PO confirm: {p.po_question}")

        tickets.append(Ticket(
            role="Product Confirmation",
            assignee="Product Team",
            condition=campaign_name,
            context=(
                f"Ket qua review UC1 cho campaign '{campaign_name}' "
                "co mot so hang muc chua available hoac chua ro trigger/loai qua."
            ),
            request_body="\n".join(pc_lines),
            related_doc=(
                f"File request dau vao cua UC1: {input_file_ref}"
            ),
            sla="1 working day",
            due_date=fmt(due_po),
        ))

    # ── TICKET 4: OPS ────────────────────────────────────────────────────────
    has_ui = bool(game_ui)

    tickets.append(Ticket(
        role="Ops",
        assignee="Ops",
        condition=campaign_name,
        context=(
            f"Campaign '{campaign_name}' (Game Type: {game_type}, "
            f"go-live T = {fmt(t)}) can duoc setup theo request da review."
        ),
        request_body=(
            "Nho Ops setup campaign theo cac hang muc da clear trong request. "
            "Cac phan con phu thuoc PO/Biz/Design se theo timeline o UC4."
        ),
        related_doc="",
        sla="10 working days",
        due_date=fmt(due_ops),
        brief=True,
    ))

    return DraftResult(
        campaign_name=campaign_name,
        go_live_date=fmt(t),
        d0=fmt(d0),
        milestone_t2=fmt(t_minus_2),
        milestone_t1=fmt(t_minus_1),
        guardrail_alert=guardrail,
        tickets=tickets,
        errors=errors,
    )
