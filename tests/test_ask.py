"""Tests for the setup guide RAG agent."""

import pytest


class TestKbSections:
    def test_load_sections_non_empty(self):
        from src.core.kb_loader import load_setup_guide_sections
        sections = load_setup_guide_sections()
        assert len(sections) > 0

    def test_sections_have_required_keys(self):
        from src.core.kb_loader import load_setup_guide_sections
        sections = load_setup_guide_sections()
        for s in sections:
            assert "id" in s
            assert "title" in s
            assert "content" in s

    def test_lucky_wheel_section_present(self):
        from src.core.kb_loader import load_setup_guide_sections
        sections = load_setup_guide_sections()
        titles = [s["title"].lower() for s in sections]
        assert any("lucky wheel" in t for t in titles)

    def test_leaderboard_section_present(self):
        from src.core.kb_loader import load_setup_guide_sections
        sections = load_setup_guide_sections()
        titles = [s["title"].lower() for s in sections]
        assert any("leaderboard" in t for t in titles)

    def test_lucky_wheel_section_has_id_a1(self):
        """Lucky Wheel section must have ID 'A1'."""
        from src.core.kb_loader import load_setup_guide_sections
        sections = load_setup_guide_sections()
        a1 = next((s for s in sections if s["id"] == "A1"), None)
        assert a1 is not None, "Section A1 not found"
        assert "lucky wheel" in a1["title"].lower()


class TestRagSearch:
    def test_lucky_wheel_query_returns_section(self):
        from src.setup_guide.rag import search
        section, score = search("cách setup Game Type lucky wheel")
        assert section is not None, f"Expected a match, got score={score}"
        assert score >= 70.0

    def test_lucky_wheel_query_returns_a1(self):
        """The ask command must resolve to section A1 for Lucky Wheel queries."""
        from src.setup_guide.rag import search
        section, score = search("cách setup Game Type lucky wheel")
        assert section is not None
        assert section["id"] == "A1", (
            f"Expected section A1 ([SCHEME] Lucky Wheel), got: {section['id']} — {section['title']}"
        )

    def test_lucky_wheel_section_id(self):
        from src.setup_guide.rag import search
        section, score = search("lucky wheel")
        assert section is not None
        assert "lucky" in section["title"].lower()

    def test_leaderboard_query_returns_section(self):
        from src.setup_guide.rag import search
        section, score = search("setup leaderboard bảng xếp hạng")
        assert section is not None
        assert score >= 70.0

    def test_gibberish_query_returns_none(self):
        from src.setup_guide.rag import search
        section, score = search("xyzabc123 không tồn tại blahlbah")
        assert section is None
        assert score < 70.0

    def test_empty_query_returns_none(self):
        from src.setup_guide.rag import search
        section, score = search("")
        assert section is None

    def test_task_module_query(self):
        from src.setup_guide.rag import search
        section, score = search("tạo task module cấu hình nhiệm vụ")
        assert section is not None
        assert score >= 70.0


class TestAnswerQuestion:
    def test_lucky_wheel_answer_has_content(self):
        from src.setup_guide.rag import answer_question
        answer = answer_question("cách setup Game Type lucky wheel")
        assert len(answer) > 50
        assert "lucky" in answer.lower()

    def test_lucky_wheel_answer_includes_source_a1(self):
        """
        ask command output must include 'A1. [SCHEME] Lucky Wheel' as source.
        """
        from src.setup_guide.rag import answer_question
        answer = answer_question("cách setup Game Type lucky wheel")
        assert "A1" in answer, f"Expected 'A1' in answer source, got:\n{answer}"
        assert "[SCHEME] Lucky Wheel" in answer or "Lucky Wheel" in answer, (
            f"Expected section title in answer, got:\n{answer}"
        )
        assert "Nguồn" in answer, f"Expected 'Nguồn' label, got:\n{answer}"

    def test_not_found_returns_po_message(self):
        from src.setup_guide.rag import answer_question
        answer = answer_question("xyz_không_tồn_tại_blabla")
        assert "không tìm thấy" in answer.lower() or "hỏi PO" in answer

    def test_answer_includes_source(self):
        from src.setup_guide.rag import answer_question
        answer = answer_question("lucky wheel")
        assert "Nguồn" in answer

    def test_leaderboard_answer_found(self):
        from src.setup_guide.rag import answer_question
        answer = answer_question("setup leaderboard")
        assert "không tìm thấy" not in answer.lower()
        assert len(answer) > 50

    def test_reward_module_query(self):
        from src.setup_guide.rag import answer_question
        answer = answer_question("tạo reward pool")
        assert len(answer) > 20

    def test_lottery_query(self):
        from src.setup_guide.rag import answer_question
        answer = answer_question("cách setup lottery xổ số")
        assert "không tìm thấy" not in answer.lower()
