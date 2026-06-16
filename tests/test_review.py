"""Tests for the campaign review agent."""

import pytest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


# ── KB loader ─────────────────────────────────────────────────────────────────

class TestKbLoader:
    def test_load_allowlist_returns_dict(self):
        from src.core.kb_loader import load_allowlist
        kb = load_allowlist()
        assert isinstance(kb, dict)

    def test_allowlist_has_required_keys(self):
        from src.core.kb_loader import load_allowlist
        kb = load_allowlist()
        assert "scheme_game_type" in kb
        assert "task_trigger" in kb
        assert "reward_type" in kb

    def test_lucky_wheel_in_allowlist(self):
        from src.core.kb_loader import load_allowlist
        kb = load_allowlist()
        game_types = [g.lower() for g in kb["scheme_game_type"]]
        assert "lucky wheel" in game_types

    def test_vietnamese_keywords_present(self):
        from src.core.kb_loader import load_allowlist
        kb = load_allowlist()
        all_keywords = []
        for kws in kb["task_trigger"].values():
            all_keywords.extend([k.lower() for k in kws])
        assert "thanh toán" in all_keywords
        assert "điểm danh" in all_keywords
        assert "mời" in all_keywords

    def test_dat_keyword_in_payment(self):
        """'đặt' must be a payment keyword per KB allowlist."""
        from src.core.kb_loader import load_allowlist
        kb = load_allowlist()
        payment_keywords = [k.lower() for k in kb["task_trigger"]["payment"]]
        assert "đặt" in payment_keywords


# ── Parser ────────────────────────────────────────────────────────────────────

class TestParser:
    _sample = _ROOT / "data" / "samples" / "campaign_request_sample_01.md"

    def test_parse_returns_dict(self):
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        assert isinstance(result, dict)

    def test_parse_campaign_name(self):
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        assert "DGS_260520_585" in result["campaign_name"]

    def test_parse_game_type(self):
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        assert result["game_type"].lower() == "lucky wheel"

    def test_parse_tasks_non_empty(self):
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        assert len(result["tasks"]) >= 1

    def test_parse_rewards_non_empty(self):
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        assert len(result["rewards"]) >= 1

    def test_sample_contains_dat_ve_task(self):
        """Sample must include 'Đặt vé máy bay hè' task."""
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        task_names = [t["name"] for t in result["tasks"]]
        assert any("Đặt vé" in n for n in task_names), (
            f"Expected 'Đặt vé máy bay hè' task in sample. Found: {task_names}"
        )

    def test_sample_contains_chup_man_hinh_task(self):
        """Sample must include 'Chụp màn hình chia sẻ campaign' task."""
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        task_names = [t["name"] for t in result["tasks"]]
        assert any("Chụp" in n for n in task_names), (
            f"Expected 'Chụp màn hình chia sẻ campaign' task in sample. Found: {task_names}"
        )

    def test_sample_contains_ve_reward(self):
        """Sample must include 'vé' reward type."""
        from src.review.parser import parse_request
        result = parse_request(self._sample)
        reward_types = [r["type"].lower() for r in result["rewards"]]
        assert any("vé" in rt for rt in reward_types), (
            f"Expected 'vé' reward in sample. Found: {reward_types}"
        )

    def test_missing_file_raises(self):
        from src.review.parser import parse_request
        with pytest.raises(FileNotFoundError):
            parse_request("nonexistent_file.md")


# ── Reviewer ──────────────────────────────────────────────────────────────────

class TestReviewer:
    _sample = str(_ROOT / "data" / "samples" / "campaign_request_sample_01.md")

    def test_review_returns_result(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        assert result is not None

    def test_review_has_campaign_name(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        assert result.campaign_name

    def test_review_supported_not_empty(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        assert len(result.supported) > 0

    def test_game_type_lucky_wheel_is_supported(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        scheme_points = [p for p in result.supported if p.category == "SCHEME"]
        assert len(scheme_points) == 1
        assert "lucky wheel" in scheme_points[0].content.lower()

    def test_known_trigger_tasks_are_supported(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        supported_tasks = [p for p in result.supported if p.category == "TASK"]
        task_names = [p.label for p in supported_tasks]
        assert any("Nạp" in n or "nạp" in n for n in task_names)
        assert any("Điểm danh" in n or "điểm danh" in n for n in task_names)

    # ── New required assertions ───────────────────────────────────────────────

    def test_dat_ve_may_bay_classified_as_payment(self):
        """'Đặt vé máy bay hè' must be classified as payment trigger (keyword 'đặt')."""
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        supported_tasks = [p for p in result.supported if p.category == "TASK"]
        dat_task = next(
            (p for p in supported_tasks if "Đặt vé" in p.label or "Đặt" in p.label),
            None,
        )
        assert dat_task is not None, (
            "'Đặt vé máy bay hè' should be in supported (payment via 'đặt'), "
            f"but found: {[p.label for p in supported_tasks]}"
        )
        assert "payment" in dat_task.detail, (
            f"Expected trigger=payment, got: {dat_task.detail}"
        )
        # keyword no longer shown in detail — trigger type is sufficient proof

    def test_chup_man_hinh_flagged_as_needs_confirm(self):
        """'Chụp màn hình chia sẻ campaign' must be in CẦN PO CONFIRM (no keyword match)."""
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        confirm_tasks = [p for p in result.needs_confirm if p.category == "TASK"]
        chup_task = next(
            (p for p in confirm_tasks if "Chụp" in p.label),
            None,
        )
        assert chup_task is not None, (
            "'Chụp màn hình chia sẻ campaign' should be in needs_confirm, "
            f"but confirm tasks are: {[p.label for p in confirm_tasks]}"
        )
        assert chup_task.po_question, "Missing PO question for flagged task"

    def test_ve_reward_flagged_as_needs_confirm(self):
        """Reward type 'vé' must be in CẦN PO CONFIRM (not in KB allowlist)."""
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        confirm_rewards = [p for p in result.needs_confirm if p.category == "REWARD"]
        ve_reward = next(
            (p for p in confirm_rewards if "vé" in p.label.lower()),
            None,
        )
        assert ve_reward is not None, (
            "Reward 'vé' should be flagged as needs_confirm. "
            f"Confirm rewards: {[p.label for p in confirm_rewards]}"
        )
        assert "Không có trong KB allowlist" in ve_reward.detail

    # ── Existing assertions ───────────────────────────────────────────────────

    def test_unknown_trigger_task_needs_confirm(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        confirm_tasks = [p for p in result.needs_confirm if p.category == "TASK"]
        assert len(confirm_tasks) >= 1

    def test_unknown_reward_needs_confirm(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        confirm_rewards = [p for p in result.needs_confirm if p.category == "REWARD"]
        assert len(confirm_rewards) >= 1

    def test_needs_confirm_points_have_po_question(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        for p in result.needs_confirm:
            assert p.po_question, f"Point {p.label} missing PO question"

    def test_total_equals_supported_plus_confirm(self):
        from src.review.reviewer import review_request
        result = review_request(self._sample)
        assert result.total == len(result.supported) + len(result.needs_confirm)

    def test_format_review_contains_headers(self):
        from src.review.reviewer import review_request, format_review
        result = review_request(self._sample)
        output = format_review(result)
        assert "=== REVIEW:" in output
        assert "ĐÃ HỖ TRỢ" in output
        assert "CẦN PO CONFIRM" in output

    def test_format_review_shows_totals(self):
        from src.review.reviewer import review_request, format_review
        result = review_request(self._sample)
        output = format_review(result)
        assert "Tổng point:" in output
        assert "Đã hỗ trợ:" in output
        assert "Cần confirm:" in output


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestReviewerEdgeCases:
    def test_unknown_game_type_flagged(self, tmp_path):
        req = tmp_path / "req.md"
        req.write_text(
            "# Campaign Request — Test Camp\n\n"
            "| Field | Value |\n|---|---|\n"
            "| Game Type | unknown_game_xyz |\n\n"
            "## Tasks\n\n"
            "| # | Task Name | Description |\n|---|---|---|\n"
            "| 1 | Thanh toán | Thanh toán hóa đơn |\n\n"
            "## Rewards\n\n"
            "| # | Reward Type | Description |\n|---|---|---|\n"
            "| 1 | xu | xu thưởng |\n",
            encoding="utf-8",
        )
        from src.review.reviewer import review_request
        result = review_request(str(req))
        scheme_flags = [p for p in result.needs_confirm if p.category == "SCHEME"]
        assert len(scheme_flags) == 1

    def test_all_supported_campaign(self, tmp_path):
        req = tmp_path / "req.md"
        req.write_text(
            "# Campaign Request — Clean Camp\n\n"
            "| Field | Value |\n|---|---|\n"
            "| Game Type | loyal |\n\n"
            "## Tasks\n\n"
            "| # | Task Name | Description |\n|---|---|---|\n"
            "| 1 | Thanh toán đơn hàng | Thanh toán để tích điểm |\n"
            "| 2 | Điểm danh | Điểm danh hàng ngày |\n\n"
            "## Rewards\n\n"
            "| # | Reward Type | Description |\n|---|---|---|\n"
            "| 1 | cashback | Hoàn tiền |\n",
            encoding="utf-8",
        )
        from src.review.reviewer import review_request
        result = review_request(str(req))
        assert len(result.needs_confirm) == 0
        assert len(result.supported) > 0
