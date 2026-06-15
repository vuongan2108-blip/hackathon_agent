"""Tests for the Timeline Campaign Assistant (UC4)."""

import pytest
from pathlib import Path
from datetime import date, timedelta

_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE = _ROOT / "data" / "samples" / "campaign_request_sample_01.md"


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _write_request(tmp_path: Path, go_live: str, extras: str = "") -> str:
    """
    Write a minimal but valid campaign request to a temp file.
    All required fields present → no Biz ticket.
    No unclear items (tasks all have known triggers) → no PC ticket.
    No Game UI section → no Design ticket.
    → Only Ops ticket generated.
    """
    content = f"""# Campaign Request — Test Campaign

| Field | Value |
|---|---|
| Campaign Name | Test Campaign |
| Game Type | lucky wheel |
| Marketing Code | TEST-001 |
| Thời gian diễn ra | {go_live} |
| Start Date | {go_live} |
| End Date | {go_live} |
| TnC Link | https://example.com/tnc |
| Mô tả chương trình | Test campaign description |

## Tasks

| # | Task Name | Description |
|---|---|---|
| 1 | Nạp điện thoại | Nạp tiền điện thoại để nhận thưởng |

## Rewards

| # | Reward Type | Description |
|---|---|---|
| 1 | voucher | 50k |

{extras}
"""
    p = tmp_path / "request.md"
    p.write_text(content, encoding="utf-8")
    return str(p)


def _write_request_with_unclear(tmp_path: Path, go_live: str) -> str:
    """Campaign with unclear task and Game UI → Biz (missing field), PC, Design, Ops tickets."""
    content = f"""# Campaign Request — Full Campaign

| Field | Value |
|---|---|
| Campaign Name | Full Campaign |
| Game Type | lucky wheel |
| Marketing Code | FULL-001 |
| Thời gian diễn ra | {go_live} |
| Start Date | {go_live} |
| End Date | {go_live} |
| TnC Link | https://example.com/tnc |

## Tasks

| # | Task Name | Description |
|---|---|---|
| 1 | Chụp màn hình | Chụp màn hình chia sẻ campaign |

## Rewards

| # | Reward Type | Description |
|---|---|---|
| 1 | voucher | 50k |

## Game UI

| Field | Value |
|---|---|
| Background | blue |
"""
    p = tmp_path / "full_request.md"
    p.write_text(content, encoding="utf-8")
    return str(p)


def _write_request_no_go_live(tmp_path: Path) -> str:
    content = """# Campaign Request — No Date Campaign

| Field | Value |
|---|---|
| Campaign Name | No Date Campaign |
| Game Type | lucky wheel |
| Marketing Code | ND-001 |
| Start Date | 2026-07-10 |
| End Date | 2026-07-20 |

## Tasks

| # | Task Name | Description |
|---|---|---|
| 1 | Nạp điện thoại | Nạp tiền |

## Rewards

| # | Reward Type | Description |
|---|---|---|
| 1 | voucher | 10k |
"""
    p = tmp_path / "no_date_request.md"
    p.write_text(content, encoding="utf-8")
    return str(p)


# ── TimelineResult basic tests ────────────────────────────────────────────────

class TestGenerateTimeline:
    def test_returns_timeline_result(self, tmp_path):
        from src.timeline.generator import generate_timeline, TimelineResult
        filepath = _write_request(tmp_path, "2026-07-10")
        result = generate_timeline(filepath)
        assert isinstance(result, TimelineResult)

    def test_campaign_name_set(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        result = generate_timeline(filepath)
        assert result.campaign_name == "Test Campaign"

    def test_d0_is_today(self, tmp_path):
        from src.timeline.generator import generate_timeline
        from datetime import datetime
        filepath = _write_request(tmp_path, "2026-07-10")
        result = generate_timeline(filepath)
        assert result.d0 == datetime.today().date()

    def test_t_matches_go_live(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        result = generate_timeline(filepath)
        assert result.t == date(2026, 7, 10)

    def test_no_errors_for_valid_request(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        result = generate_timeline(filepath)
        assert result.errors == []

    def test_missing_go_live_returns_error(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request_no_go_live(tmp_path)
        result = generate_timeline(filepath)
        assert result.errors
        assert "go-live" in result.errors[0].lower() or "ngày" in result.errors[0]

    def test_file_not_found_raises(self):
        from src.timeline.generator import generate_timeline
        with pytest.raises(FileNotFoundError):
            generate_timeline("/nonexistent/path/request.md")


# ── Render: header and structure ──────────────────────────────────────────────

class TestRenderStructure:
    def test_render_contains_campaign_name(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "Test Campaign" in output

    def test_render_contains_d0_and_t_header(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "D0:" in output
        assert "T (go-live):" in output

    def test_render_contains_milestones_line(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "T-2" in output
        assert "T-1" in output
        assert "GO LIVE" in output

    def test_render_error_output_when_missing_go_live(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request_no_go_live(tmp_path)
        output = generate_timeline(filepath).render()
        assert "[ERROR]" in output

    def test_render_contains_markdown_table(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        # Markdown table rows start with |
        table_rows = [ln for ln in output.splitlines() if ln.startswith("|")]
        assert len(table_rows) >= 6  # header + sep + 4 actor rows + milestone row

    def test_render_contains_review_note(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "Ops: review timeline below" in output
        assert "chạy lại UC3" in output


# ── Fixed 4 rows always present ───────────────────────────────────────────────

class TestFixedRows:
    def _row_names(self, output: str) -> list[str]:
        """Extract actor names from table rows (lines starting with | <name>)."""
        rows = []
        for line in output.splitlines():
            if line.startswith("|") and not line.startswith("|---"):
                first_cell = line.split("|")[1].strip()
                rows.append(first_cell)
        return rows

    def test_biz_row_always_present(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        rows = self._row_names(output)
        assert "Biz" in rows

    def test_design_row_always_present(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        rows = self._row_names(output)
        assert "Design" in rows

    def test_pc_row_always_present(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        rows = self._row_names(output)
        assert "Product Confirmation" in rows

    def test_ops_row_always_present(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        rows = self._row_names(output)
        assert "Ops" in rows

    def test_all_four_rows_present_minimal_request(self, tmp_path):
        """Even with minimal input (only Ops ticket), all 4 rows appear."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        rows = self._row_names(output)
        assert "Biz" in rows
        assert "Design" in rows
        assert "Product Confirmation" in rows
        assert "Ops" in rows

    def test_all_four_rows_present_full_request(self, tmp_path):
        """Full request (all 4 tickets generated) — all 4 rows appear."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request_with_unclear(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        rows = self._row_names(output)
        assert "Biz" in rows
        assert "Design" in rows
        assert "Product Confirmation" in rows
        assert "Ops" in rows

    def test_milestone_row_present(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        rows = self._row_names(output)
        assert "— Milestones —" in rows


# ── không phát sinh ───────────────────────────────────────────────────────────

class TestKhongPhatSinh:
    def _ops_row_line(self, output: str) -> str:
        for line in output.splitlines():
            if line.startswith("| Ops"):
                return line
        return ""

    def test_biz_row_khong_phat_sinh_when_all_fields_present(self, tmp_path):
        """All required fields present → no Biz ticket → row shows không phát sinh."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        biz_line = next(
            (ln for ln in output.splitlines() if ln.startswith("| Biz")), ""
        )
        assert "không phát sinh" in biz_line

    def test_design_row_khong_phat_sinh_when_no_game_ui(self, tmp_path):
        """No Game UI → no Design ticket → row shows không phát sinh."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        design_line = next(
            (ln for ln in output.splitlines() if ln.startswith("| Design")), ""
        )
        assert "không phát sinh" in design_line

    def test_pc_row_khong_phat_sinh_when_no_unclear_items(self, tmp_path):
        """No unclear items → no PC ticket → row shows không phát sinh."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        pc_line = next(
            (ln for ln in output.splitlines() if ln.startswith("| Product Confirmation")), ""
        )
        assert "không phát sinh" in pc_line

    def test_ops_unclear_track_khong_phat_sinh_when_no_unclear(self, tmp_path):
        """No unclear items → Ops chưa-clear track shows không phát sinh."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        ops_line = self._ops_row_line(output)
        assert "không phát sinh" in ops_line

    def test_ops_ui_track_khong_phat_sinh_when_no_game_ui(self, tmp_path):
        """No Game UI → Ops UI track shows không phát sinh."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        ops_line = self._ops_row_line(output)
        # Both unclear and UI tracks are không phát sinh in this fixture
        assert ops_line.count("không phát sinh") >= 2


# ── Ops 3-track D0 rendering ──────────────────────────────────────────────────

class TestOpsD0Rendering:
    def _ops_row_line(self, output: str) -> str:
        for line in output.splitlines():
            if line.startswith("| Ops"):
                return line
        return ""

    def test_ops_clear_starts_at_d0(self, tmp_path):
        """At D0, Ops clear track shows ▓."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request_with_unclear(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        ops_line = self._ops_row_line(output)
        # D0 column cell contains ▓ clear
        assert "▓ clear" in ops_line

    def test_ops_unclear_waits_for_pc_at_d0(self, tmp_path):
        """At D0, Ops chưa-clear track is waiting for PC (not started)."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request_with_unclear(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        ops_line = self._ops_row_line(output)
        # D0 column cell should have · chờ PC, not ▓ chưa-clear
        assert "chờ PC" in ops_line
        # Should NOT show chưa-clear started at D0
        assert "▓ chưa-clear" not in ops_line.split("|")[2]  # D0 col is cell index 2

    def test_ops_ui_waits_for_design_at_d0(self, tmp_path):
        """At D0, Ops UI track is waiting for Design (not started)."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request_with_unclear(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        ops_line = self._ops_row_line(output)
        assert "chờ Design" in ops_line
        assert "▓ UI" not in ops_line.split("|")[2]  # D0 col is cell index 2

    def test_ops_three_tracks_joined_in_d0_cell(self, tmp_path):
        """D0 Ops cell contains all 3 tracks separated by <br>."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request_with_unclear(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        ops_line = self._ops_row_line(output)
        d0_cell = ops_line.split("|")[2]  # first data column after actor name
        assert d0_cell.count("<br>") == 2  # exactly 2 separators = 3 tracks


# ── Column count ──────────────────────────────────────────────────────────────

class TestColumnCount:
    def test_column_count_equals_d0_to_t_inclusive(self, tmp_path):
        """Number of date columns = (T - D0).days + 1."""
        from src.timeline.generator import generate_timeline
        from datetime import datetime
        filepath = _write_request(tmp_path, "2026-07-10")
        result = generate_timeline(filepath)
        output = result.render()

        expected_cols = (result.t - result.d0).days + 1

        # Count columns from header row (first | row)
        header_line = next(ln for ln in output.splitlines() if ln.startswith("| Actor"))
        # Number of | separators - 1 = number of cells; subtract 1 for actor column
        num_data_cols = header_line.count("|") - 2  # strips leading/trailing |
        assert num_data_cols == expected_cols

    def test_d0_column_header_present(self, tmp_path):
        """Header row contains a 'D0' column label."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        header_line = next(ln for ln in output.splitlines() if ln.startswith("| Actor"))
        assert "D0" in header_line

    def test_t_column_header_present(self, tmp_path):
        """Header row contains a 'T' column label for go-live date."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        header_line = next(ln for ln in output.splitlines() if ln.startswith("| Actor"))
        assert "T 10/07" in header_line

    def test_no_week_grouping_in_headers(self, tmp_path):
        """No week labels (W1, W2, Week) in column headers."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        header_line = next(ln for ln in output.splitlines() if ln.startswith("| Actor"))
        assert "W1" not in header_line
        assert "W2" not in header_line
        assert "Week" not in header_line.lower()


# ── Guardrail propagation ─────────────────────────────────────────────────────

class TestGuardrailPropagation:
    def test_guardrail_appended_when_timeline_short(self, tmp_path):
        """When (T - D0) < 14 days, GUARDRAIL text appears in output."""
        from src.timeline.generator import generate_timeline
        from datetime import datetime, timedelta
        short_t = (datetime.today().date() + timedelta(days=5)).strftime("%Y-%m-%d")
        filepath = _write_request(tmp_path, short_t)
        output = generate_timeline(filepath).render()
        assert "GUARDRAIL" in output

    def test_no_guardrail_when_timeline_sufficient(self, tmp_path):
        """When (T - D0) >= 14 days, no GUARDRAIL text."""
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "GUARDRAIL" not in output


# ── Dependencies note ─────────────────────────────────────────────────────────

class TestDependenciesNote:
    def test_dependencies_section_present(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "📌 Dependencies:" in output

    def test_pc_dependency_noted_when_unclear_items_exist(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request_with_unclear(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "Ops–chưa-clear" in output
        assert "Product Confirmation" in output

    def test_design_dependency_noted_when_game_ui_exists(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request_with_unclear(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "Ops–UI" in output
        assert "Design" in output

    def test_no_pc_dependency_when_all_items_clear(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "Ops–chưa-clear" not in output

    def test_no_design_dependency_when_no_game_ui(self, tmp_path):
        from src.timeline.generator import generate_timeline
        filepath = _write_request(tmp_path, "2026-07-10")
        output = generate_timeline(filepath).render()
        assert "Ops–UI" not in output


# ── Integration with full sample ──────────────────────────────────────────────

class TestIntegrationWithSample:
    def test_sample_01_generates_without_error(self):
        from src.timeline.generator import generate_timeline
        result = generate_timeline(str(_SAMPLE))
        assert result.errors == []

    def test_sample_01_render_contains_all_four_rows(self):
        from src.timeline.generator import generate_timeline
        output = generate_timeline(str(_SAMPLE)).render()
        for actor in ["Biz", "Design", "Product Confirmation", "Ops"]:
            assert actor in output

    def test_sample_01_ops_clear_starts_d0(self):
        from src.timeline.generator import generate_timeline
        output = generate_timeline(str(_SAMPLE)).render()
        ops_line = next(
            (ln for ln in output.splitlines() if ln.startswith("| Ops")), ""
        )
        assert "▓ clear" in ops_line

    def test_sample_01_review_note_present(self):
        from src.timeline.generator import generate_timeline
        output = generate_timeline(str(_SAMPLE)).render()
        assert "Ops: review timeline below" in output

    def test_sample_01_go_live_column_present(self):
        from src.timeline.generator import generate_timeline
        output = generate_timeline(str(_SAMPLE)).render()
        # T = 10/07/2026 → column header "T 10/07"
        assert "T 10/07" in output
