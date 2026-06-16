"""
Setup Guide RAG — keyword-based search over local KB.
No external API calls. Score threshold = 70.
"""

from __future__ import annotations

import re
from src.core.kb_loader import load_setup_guide_sections

_THRESHOLD = 70.0

# Vietnamese stop words to exclude from scoring
_STOP_WORDS = {
    "cách", "của", "và", "cho", "với", "trong", "trên", "về", "là",
    "có", "không", "được", "này", "đó", "một", "các", "khi",
    "setup", "cài", "đặt", "hỏi", "muốn", "biết", "làm",
}


def _tokenize(text: str) -> list[str]:
    """Lowercase and split on whitespace/punctuation; filter stop words."""
    tokens = re.findall(r"[\w]+", text.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) >= 2]


def _score_section(query_tokens: list[str], section: dict) -> float:
    """
    Score a KB section against query tokens.
    Returns 0–100.

    Scoring priority:
    1. Title / alias exact or partial match → score 90–100
    2. Query token overlap with full section content → 0–85
    """
    if not query_tokens:
        return 0.0

    query_set = set(query_tokens)

    # ── Check aliases (high confidence) ──────────────────────────────────────
    for alias in section.get("aliases", []):
        alias_tokens = set(_tokenize(alias))
        if not alias_tokens:
            continue
        overlap = len(query_set & alias_tokens)
        ratio = overlap / len(alias_tokens)
        if ratio >= 0.5:
            return 90.0 + min(10.0, ratio * 10)

    # ── Check section title ───────────────────────────────────────────────────
    title_tokens = set(_tokenize(section.get("title", "")))
    if title_tokens:
        title_overlap = len(query_set & title_tokens)
        title_ratio = title_overlap / len(title_tokens)
        if title_ratio >= 0.5:
            return 85.0

    # ── Fallback: content keyword overlap ─────────────────────────────────────
    content_tokens = set(_tokenize(section.get("content", "")))
    if not content_tokens:
        return 0.0

    matching = len(query_set & content_tokens)
    # Score = fraction of query tokens found in section, scaled to 0–85
    score = (matching / len(query_set)) * 85.0
    return round(score, 1)


def search(question: str) -> tuple[dict | None, float]:
    """
    Find the best matching KB section for a question.

    Returns (section, score). section is None if best score < threshold.
    """
    sections = load_setup_guide_sections()
    query_tokens = _tokenize(question)

    if not query_tokens:
        return None, 0.0

    best_section = None
    best_score = 0.0

    for section in sections:
        score = _score_section(query_tokens, section)
        if score > best_score:
            best_score = score
            best_section = section

    if best_score < _THRESHOLD:
        return None, best_score

    return best_section, best_score


def answer_question(question: str) -> str:
    """
    Answer a setup question using the local KB.

    Returns formatted answer string with source, or "cần hỏi PO" message.
    """
    section, score = search(question)

    if section is None:
        return (
            "Mình không tìm thấy thông tin này trong KB nội bộ. "
            "Bạn cần hỏi PO để xác nhận nhé."
        )

    # Build answer from section content
    lines = []
    lines.append(section["title"])
    lines.append("")

    # Extract readable content (skip metadata lines)
    content_lines = []
    for line in section["content"].splitlines():
        stripped = line.strip()
        # Skip alias/source/status/note metadata lines at top of section
        if re.match(r"^- (source|status|aliases|precondition|note):", stripped):
            continue
        if stripped.startswith(">"):
            continue
        # Strip markdown bold markers from content
        content_lines.append(line.replace("**", ""))

    lines.append("\n".join(content_lines).strip())
    lines.append("")

    # Source — display internal KB reference only, no raw URL
    section_ref = f"{section['id']}. {section['title']}"
    lines.append(f"Nguồn KB nội bộ: {section_ref}")

    return "\n".join(lines)
