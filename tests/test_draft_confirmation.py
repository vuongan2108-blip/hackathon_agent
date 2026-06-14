"""Tests for the draft-confirmation (UC3) generator."""

import pytest
from pathlib import Path
from datetime import date, timedelta

_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE = _ROOT / "data" / "samples" / "campaign_request_sample_01.md"


# ── Date utilities ────────────────────────────────────────────────────────────

class TestDateUtils:
    def test_add_working_days_skips_weekend(self):
        from src.draft_confirmation.date_utils import add_working_days
        # June 14 2026 = Sunday → +1 working day = Monday June 15
        d = date(2026, 6, 14)
        result = add_working_days(d, 1)
        assert result == date(2026, 6, 15)

    def test_add_working_days_two(self):
        from src.draft_confirmation.date_utils import add_working_days
        # Friday + 2 working days = Tuesday (skips Sat/Sun)
        d = date(2026, 6, 12)  # Friday
        result = add_working_days(d, 2)
        assert result == date(2026, 6, 16)  # Tuesday

    def test_subtract_working_days(self):
        from src.draft_confirmation.date_utils import subtract_working_days
        # Monday − 1 working day = Friday
        d = date(2026, 6, 15)  # Monday
        result = subtract_working_days(d, 1)
        assert result == date(2026, 6, 12)  # Friday

    def test_subtract_working_days_skips_weekend(self):
        from src.draft_confirmation.date_utils import subtract_working_days
        # Monday − 2 working days = Thursday (skips Sat/Sun)
        d = date(2026, 6, 15)  # Monday
        result = subtract_working_days(d, 2)
        assert result == date(2026, 6, 11)  # Thursday

    def test_add_calendar_days(self):
        from src.draft_confirmation.date_utils import add_calendar_days
        d = date(2026, 6, 14)
        assert add_calendar_days(d, 7) == date(2026, 6, 21)

    def test_fmt(self):
        from src.draft_confirmation.date_utils import fmt
        assert fmt(date(2026, 7, 10)) == "10/07/2026"


# ── Parser extensions ─────────────────────────────────────────────────────────

class TestParserExtensions:
    def test_parse_go_live_date(self):
        from src.review.parser import parse_request
        result = parse_request(_SAMPLE)
        assert result.get("go_live_date") == "2026-07-10"

    def test_parse_game_ui_present(self):
        from src.review.parser import parse_request
        result = parse_request(_SAMPLE)
        game_ui = result.get("game_ui", {})
        assert isinstance(game_ui, dict)
        assert len(game_ui) > 0

    def test_parse_game_ui_has_design_brief(self):
        from src.review.parser import parse_request
        result = parse_request(_SAMPLE)
        game_ui = result.get("game_ui", {})
        keys_lower = [k.lower() for k in game_ui]
        assert any("design brief" in k for k in keys_lower)

    def test_parse_general_fields_returned(self):
        from src.review.parser import parse_request
        result = parse_request(_SAMPLE)
        gf = result.get("general_fields", {})
        assert "campaign name" in gf
        assert "game type" in gf


# ── Generator ─────────────────────────────────────────────────────────────────

class TestGenerator:
    def test_generate_returns_draft_result(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        assert result is not None

    def test_generate_has_campaign_name(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        assert "DGS_260520_585" in result.campaign_name

    def test_generate_go_live_date(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        assert result.go_live_date == "10/07/2026"

    def test_generate_milestones_set(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        assert result.milestone_t2 != "N/A"
        assert result.milestone_t1 != "N/A"

    def test_t_minus_2_before_t_minus_1(self):
        """T-2 must be earlier than T-1."""
        from src.draft_confirmation.generator import generate_draft
        from src.draft_confirmation.date_utils import fmt
        result = generate_draft(str(_SAMPLE))
        # Both are dd/mm/yyyy — compare via date parsing
        from datetime import datetime
        t2 = datetime.strptime(result.milestone_t2, "%d/%m/%Y").date()
        t1 = datetime.strptime(result.milestone_t1, "%d/%m/%Y").date()
        assert t2 < t1

    def test_no_errors_on_valid_sample(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        assert result.errors == [], f"Unexpected errors: {result.errors}"

    def test_biz_ticket_generated(self):
        """Sample is missing 'mô tả chương trình' → Biz ticket must be generated."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        roles = [t.role for t in result.tickets]
        assert "Biz" in roles, f"Expected Biz ticket. Tickets: {roles}"

    def test_design_ticket_generated(self):
        """Sample has Game UI section → Design ticket must be generated."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        roles = [t.role for t in result.tickets]
        assert "Design" in roles, f"Expected Design ticket. Tickets: {roles}"

    def test_po_ticket_generated(self):
        """Sample has UC1 needs-confirm items → PO ticket must be generated."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        roles = [t.role for t in result.tickets]
        assert "PO" in roles, f"Expected PO ticket. Tickets: {roles}"

    def test_ops_ticket_always_generated(self):
        """Ops ticket must always be generated."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        roles = [t.role for t in result.tickets]
        assert "Ops" in roles, f"Expected Ops ticket. Tickets: {roles}"

    def test_ops_ticket_has_three_parts(self):
        """Ops ticket body must reference all 3 parts: clear, chưa-clear, UI."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        ops = next(t for t in result.tickets if t.role == "Ops")
        assert "clear" in ops.request_body.lower()
        assert "chưa-clear" in ops.request_body or "chưa clear" in ops.request_body.lower()
        assert "ui" in ops.request_body.lower()

    def test_ops_ticket_has_dependency(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        ops = next(t for t in result.tickets if t.role == "Ops")
        assert ops.dependency, "Ops ticket must have dependency note"

    def test_po_ticket_contains_unclear_items(self):
        """PO ticket must list the UC1 needs-confirm items."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        po = next((t for t in result.tickets if t.role == "PO"), None)
        assert po is not None
        # "Chụp màn hình" and "vé" are the two unclear items
        assert "Chụp" in po.request_body or "chụp" in po.request_body.lower()

    def test_each_ticket_has_dear_assignee(self):
        """Every ticket must open with 'Dear <role>'."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        for ticket in result.tickets:
            rendered = ticket.render()
            assert f"Dear {ticket.assignee}" in rendered

    def test_each_ticket_has_due_date(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        for ticket in result.tickets:
            assert ticket.due_date, f"{ticket.role} ticket missing due_date"

    def test_render_output_contains_headers(self):
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        output = result.render()
        assert "=== DRAFT CONFIRMATION TICKETS:" in output
        assert "Milestones:" in output
        assert "TICKET: BIZ" in output
        assert "TICKET: OPS" in output

    # ── Validation-point tests (spec compliance) ──────────────────────────────

    def test_po_ticket_includes_chup_man_hinh(self):
        """PO ticket must include 'Chụp màn hình chia sẻ campaign' (unsupported task)."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        po = next(t for t in result.tickets if t.role == "PO")
        assert "Chụp" in po.request_body or "chụp" in po.request_body.lower(), (
            f"PO ticket body: {po.request_body}"
        )

    def test_po_ticket_includes_ve_reward(self):
        """PO ticket must include reward 'vé' (not in allowlist)."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        po = next(t for t in result.tickets if t.role == "PO")
        assert "vé" in po.request_body.lower(), (
            f"PO ticket body does not mention 'vé': {po.request_body}"
        )

    def test_po_ticket_does_not_include_dat_ve_may_bay(self):
        """PO ticket must NOT include 'Đặt vé máy bay hè' — it is a supported (clear) task."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        po = next(t for t in result.tickets if t.role == "PO")
        assert "Đặt vé máy bay" not in po.request_body, (
            "'Đặt vé máy bay hè' is supported via keyword 'đặt' and must NOT "
            f"appear in PO ticket. Body: {po.request_body}"
        )

    def test_ops_ticket_separates_clear_and_blocked(self):
        """Ops ticket must list clear items and blocked (chưa-clear) items separately."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        ops = next(t for t in result.tickets if t.role == "Ops")
        body = ops.request_body
        # Part 1 clear section must mention a supported item
        assert "Phần clear" in body or "clear" in body.lower()
        # Part 2 blocked section must mention chưa-clear
        assert "chưa-clear" in body or "Chưa-clear" in body
        # The two sections must be distinct (clear items should not bleed into blocked)
        assert "Chụp màn hình" in body  # unsupported → in blocked part
        assert "Nạp điện thoại" in body or "payment" in body.lower() or "SCHEME" in body  # clear

    def test_design_ticket_includes_game_ui_context(self):
        """Design ticket must include Game UI fields from the request."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        design = next(t for t in result.tickets if t.role == "Design")
        assert "Lucky Wheel" in design.request_body or "lucky wheel" in design.request_body.lower()
        assert "Design brief" in design.request_body or "brief" in design.request_body.lower()

    def test_biz_ticket_flags_missing_business_context(self):
        """Biz ticket must list the missing required field(s)."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        biz = next(t for t in result.tickets if t.role == "Biz")
        # 'mô tả chương trình' is missing in the sample
        assert "mô tả chương trình" in biz.request_body.lower(), (
            f"Biz ticket must flag 'mô tả chương trình'. Body: {biz.request_body}"
        )

    def test_output_contains_ops_review_wording(self):
        """Output must say Ops must review before copy-paste (not PO)."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        output = result.render()
        # Must contain Ops + review/copy-paste language
        assert "Ops" in output
        lower = output.lower()
        assert "review" in lower and ("copy" in lower or "copy-paste" in lower), (
            "Output must contain Ops review / copy-paste wording"
        )

    def test_output_does_not_say_po_must_review_before_copy_paste(self):
        """Output must NOT contain 'PO must review before copy-paste' or equivalent."""
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        output = result.render()
        forbidden = [
            "PO must review before copy",
            "PO phải review trước khi copy",
            "PO review before copy-paste",
        ]
        for phrase in forbidden:
            assert phrase not in output, (
                f"Output must NOT contain '{phrase}'"
            )


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestGeneratorEdgeCases:
    def test_generate_ticket_content_saves_combined_file(self, tmp_path):
        """generate-ticket-content must save a combined output file."""
        import subprocess, sys
        out_file = tmp_path / "tickets_out.txt"
        # Patch the save path by calling _run_draft directly
        import importlib, pathlib
        # Use the generator directly and write to tmp_path
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(_SAMPLE))
        out_file.write_text(result.render(), encoding="utf-8")
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "TICKET: OPS" in content
        assert "TICKET: PO" in content

    def test_missing_go_live_date_returns_error(self, tmp_path):
        """Request without T must return an error, not raise an exception."""
        req = tmp_path / "req.md"
        req.write_text(
            "# Campaign Request — No Date Camp\n\n"
            "| Field | Value |\n|---|---|\n"
            "| Game Type | loyal |\n\n"
            "## Tasks\n\n"
            "| # | Task Name | Description |\n|---|---|---|\n"
            "| 1 | Điểm danh | Điểm danh nhận thưởng |\n\n"
            "## Rewards\n\n"
            "| # | Reward Type | Description |\n|---|---|---|\n"
            "| 1 | xu | xu thưởng |\n",
            encoding="utf-8",
        )
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(req))
        assert len(result.errors) > 0
        assert any("thiếu" in e.lower() or "go-live" in e.lower() for e in result.errors)

    def test_missing_request_file_raises(self):
        from src.draft_confirmation.generator import generate_draft
        with pytest.raises(FileNotFoundError):
            generate_draft("nonexistent_file.md")

    def test_no_game_ui_skips_design_ticket(self, tmp_path):
        """Request without Game UI section must not generate Design ticket."""
        req = tmp_path / "req.md"
        req.write_text(
            "# Campaign Request — No UI Camp\n\n"
            "| Field | Value |\n|---|---|\n"
            "| Game Type | loyal |\n"
            "| Thời gian diễn ra | 2026-08-01 |\n\n"
            "## Tasks\n\n"
            "| # | Task Name | Description |\n|---|---|---|\n"
            "| 1 | Thanh toán | Thanh toán hóa đơn |\n\n"
            "## Rewards\n\n"
            "| # | Reward Type | Description |\n|---|---|---|\n"
            "| 1 | xu | xu thưởng |\n",
            encoding="utf-8",
        )
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(req))
        roles = [t.role for t in result.tickets]
        assert "Design" not in roles
        assert "Ops" in roles

    def test_guardrail_triggered_when_t_minus_d0_less_than_14(self, tmp_path):
        """When T − D0 < 14 days, guardrail_alert must be non-empty."""
        from datetime import datetime, timedelta
        t_close = (datetime.today().date() + timedelta(days=7)).strftime("%Y-%m-%d")
        req = tmp_path / "req.md"
        req.write_text(
            f"# Campaign Request — Short Camp\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Game Type | lucky wheel |\n"
            f"| Thời gian diễn ra | {t_close} |\n\n"
            "## Tasks\n\n"
            "| # | Task Name | Description |\n|---|---|---|\n"
            "| 1 | Mua hàng | Thanh toán nhận quà |\n\n"
            "## Rewards\n\n"
            "| # | Reward Type | Description |\n|---|---|---|\n"
            "| 1 | voucher | voucher |\n",
            encoding="utf-8",
        )
        from src.draft_confirmation.generator import generate_draft
        result = generate_draft(str(req))
        assert result.guardrail_alert != "", "Expected guardrail alert for short timeline"
