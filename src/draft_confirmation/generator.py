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
    add_calendar_days,
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


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Ticket:
    role: str          # Biz / Design / PO / Ops
    assignee: str      # same as role (placeholder for Ops to fill)
    condition: str     # why this ticket was generated
    context: str
    request_body: str
    related_doc: str
    sla: str
    due_date: str
    dependency: str = ""

    def render(self) -> str:
        lines = [
            f"--- TICKET: {self.role.upper()} ---",
            f"Dear {self.assignee},",
            f"Để support cho campaign [{self.condition}],",
            f"nhờ bạn support giúp:",
            "",
            f"• Context:      {self.context}",
            f"• Request:      {self.request_body}",
            f"• Related doc:  {self.related_doc}",
            f"• Timeline:     SLA {self.sla} — due {self.due_date}",
        ]
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
        lines = []
        lines.append(f"=== DRAFT CONFIRMATION TICKETS: {self.campaign_name} ===")
        lines.append(
            f"Generated: {self.d0} | T (go-live): {self.go_live_date}"
        )
        lines.append(
            f"Milestones: T−2 = {self.milestone_t2} (gửi link test)"
            f" | T−1 = {self.milestone_t1} (update theo feedback)"
            f" | T = {self.go_live_date} (go live)"
        )
        lines.append(
            "⚠️  Ops phải review nội dung bên dưới trước khi copy-paste sang Jira. "
            "Agent chỉ soạn nháp — KHÔNG ghi Jira tự động."
        )

        if self.guardrail_alert:
            lines.append(f"\n⚠️  GUARDRAIL: {self.guardrail_alert}")

        if self.errors:
            lines.append("")
            for e in self.errors:
                lines.append(f"[ERROR] {e}")

        lines.append("")
        for ticket in self.tickets:
            lines.append(ticket.render())
            lines.append("")

        lines.append(
            "--- END OF DRAFT ---\n"
            "Ops: review xong thì copy từng ticket vào Jira. "
            "Điền tên người/nhóm thật vào chỗ [assignee] trước khi gửi."
        )
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

    d0: date = datetime.today().date()
    errors: list[str] = []

    # ── Resolve T (go-live date) ──────────────────────────────────────────────
    if not go_live_str:
        return DraftResult(
            campaign_name=campaign_name,
            go_live_date="(chưa có)",
            d0=fmt(d0),
            milestone_t2="N/A",
            milestone_t1="N/A",
            guardrail_alert="",
            errors=[
                "Thiếu ngày go-live (Thời gian diễn ra) trong request. "
                "Đây là thiếu thông tin request — Ops cần sinh Biz ticket "
                "hỏi biz bổ sung, sau đó chạy lại lệnh này."
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
                f"Không đọc được ngày go-live '{go_live_str}'. "
                "Cần format YYYY-MM-DD."
            ],
        )

    # ── Timeline milestones ───────────────────────────────────────────────────
    t_minus_2: date = subtract_working_days(t, 2)
    t_minus_1: date = subtract_working_days(t, 1)

    # ── Due dates per SLA ─────────────────────────────────────────────────────
    due_biz: date = add_working_days(d0, 1)
    due_po: date = add_working_days(d0, 1)
    due_design: date = add_calendar_days(d0, 7)
    due_ops: date = add_calendar_days(d0, 14)

    # ── Guardrail: (T − D0) < 14 calendar days ───────────────────────────────
    delta_days = (t - d0).days
    guardrail = ""
    if delta_days < 14:
        guardrail = (
            f"(T − D0) = {delta_days} ngày < 2 tuần. "
            "Timeline ngắn — Ops cần điều chỉnh lịch; "
            "timeline xuất bên dưới giữ nguyên để tham khảo."
        )

    # ── UC1: run review internally ────────────────────────────────────────────
    uc1: ReviewResult = review_request(filepath)
    unclear_items = [p for p in uc1.needs_confirm]
    clear_items = [p for p in uc1.supported]

    # ── UC2: setup guide lookup for game type (clear items) ──────────────────
    setup_guide_answer = answer_question(f"cách setup {game_type}")
    if "không tìm thấy" in setup_guide_answer.lower():
        setup_guide_ref = "Không có hướng dẫn trong KB nội bộ — hỏi PO."
    else:
        # Extract just the Nguồn line
        nguon_line = next(
            (ln for ln in setup_guide_answer.splitlines() if "Nguồn" in ln),
            setup_guide_answer.split("\n")[0],
        )
        setup_guide_ref = nguon_line.replace("**", "").strip()

    # ── Build tickets ─────────────────────────────────────────────────────────
    tickets: list[Ticket] = []

    # TICKET 1 — BIZ (missing required fields or missing descriptions)
    missing_fields = [
        f for f in REQUIRED_FIELDS
        if f not in general_fields or not general_fields[f].strip()
    ]
    if missing_fields:
        field_list = "; ".join(f'"{f}"' for f in missing_fields)
        tickets.append(Ticket(
            role="Biz",
            assignee="Biz",
            condition=campaign_name,
            context=(
                f"Campaign '{campaign_name}' (Game Type: {game_type}) "
                "đang trong giai đoạn chuẩn bị. "
                "Một số field trong request còn thiếu hoặc thiếu mô tả."
            ),
            request_body=(
                f"Nhờ bạn input lại đầy đủ các field còn thiếu/thiếu mô tả: "
                f"{field_list}."
            ),
            related_doc="File request đính kèm; template: template_request_campaign_v1",
            sla="1 working day",
            due_date=fmt(due_biz),
        ))

    # TICKET 2 — DESIGN (Game UI section present)
    if game_ui:
        ui_brief_lines = [f"{k}: {v}" for k, v in game_ui.items()]
        ui_brief = "; ".join(ui_brief_lines)
        tickets.append(Ticket(
            role="Design",
            assignee="Design",
            condition=campaign_name,
            context=(
                f"Campaign '{campaign_name}' dùng Game Type: {game_type}. "
                "Request đã có phần Game UI cần thiết kế."
            ),
            request_body=(
                f"Nhờ bạn thiết kế UI theo Game UI brief: {ui_brief}."
            ),
            related_doc="File request đính kèm; KB: " + setup_guide_ref,
            sla="7 ngày (calendar)",
            due_date=fmt(due_design),
        ))

    # TICKET 3 — PO (unclear / not-available items from UC1)
    if unclear_items:
        unclear_list = "; ".join(
            f'[{p.category}] {p.label}: {p.detail}' for p in unclear_items
        )
        tickets.append(Ticket(
            role="PO",
            assignee="PO",
            condition=campaign_name,
            context=(
                f"Kết quả review UC1 cho campaign '{campaign_name}' "
                "có một số hạng mục chưa available hoặc chưa rõ trigger."
            ),
            request_body=(
                f"Nhờ bạn confirm các điểm chưa available/chưa rõ: "
                f"{unclear_list}."
            ),
            related_doc="Output UC1 (review) đính kèm; file request đính kèm",
            sla="1 working day",
            due_date=fmt(due_po),
        ))

    # TICKET 4 — OPS (always generated; 3 parts)
    clear_summary = (
        "; ".join(f'[{p.category}] {p.label}' for p in clear_items)
        if clear_items else "(không có)"
    )
    unclear_summary = (
        "; ".join(f'[{p.category}] {p.label}' for p in unclear_items)
        if unclear_items else "(không có)"
    )
    has_ui = bool(game_ui)

    ops_request_lines = [
        "Setup campaign theo request đính kèm. Ba phần tiến hành như sau:",
        f"  1. [Phần clear — start ngay D0={fmt(d0)}]",
        f"     Hạng mục: {clear_summary}",
        f"     Tham khảo: {setup_guide_ref}",
        f"  2. [Phần chưa-clear — chờ PO ticket xong, due {fmt(due_po)}]",
        f"     Hạng mục: {unclear_summary}",
    ]
    if has_ui:
        ops_request_lines += [
            f"  3. [Phần config UI — chờ Design ticket xong, due {fmt(due_design)}]",
            f"     Game UI: {'; '.join(f'{k}: {v}' for k, v in game_ui.items())}",
        ]
    else:
        ops_request_lines.append(
            "  3. [Phần config UI] — Không có section Game UI trong request; bỏ qua."
        )

    depend_note = f"Phần 2 depend PO ticket (due {fmt(due_po)})"
    if has_ui:
        depend_note += f"; Phần 3 depend Design ticket (due {fmt(due_design)})"

    tickets.append(Ticket(
        role="Ops",
        assignee="Ops",
        condition=campaign_name,
        context=(
            f"Campaign '{campaign_name}' (Game Type: {game_type}, "
            f"go-live T = {fmt(t)}). "
            "Bộ ticket điều phối đã được soạn đầy đủ."
        ),
        request_body="\n".join(ops_request_lines),
        related_doc=(
            "File request đính kèm (Confluence/local); "
            f"KB setup guide: {setup_guide_ref}"
        ),
        sla="2 tuần (calendar)",
        due_date=fmt(due_ops),
        dependency=depend_note,
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
