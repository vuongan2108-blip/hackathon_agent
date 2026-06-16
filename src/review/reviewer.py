"""Review agent — checks campaign request against KB allowlist."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Literal

from src.core.kb_loader import load_allowlist
from src.review.parser import parse_request


# ── Helpers ──────────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    """Lowercase + strip; keep Vietnamese diacritics for keyword matching."""
    return text.lower().strip()


def _find_trigger(task_name: str, task_desc: str, trigger_map: dict[str, list[str]]) -> tuple[str | None, str | None]:
    """
    Scan task name+description for trigger keywords.

    Returns (trigger_type, matched_keyword) or (None, None).
    If multiple triggers match, returns the first match found.
    """
    combined = _norm(f"{task_name} {task_desc}")
    matches = []
    for trigger, keywords in trigger_map.items():
        for kw in keywords:
            if kw in combined:
                matches.append((trigger, kw))
    if not matches:
        return None, None
    if len(matches) == 1:
        return matches[0]
    # Multiple matches — still return all; caller can inspect via matches list
    return matches[0][0], matches[0][1]


# ── Result data classes ───────────────────────────────────────────────────────

@dataclass
class ReviewPoint:
    category: Literal["SCHEME", "TASK", "REWARD"]
    label: str         # e.g. "Game Type", 'Task "Nạp điện thoại"', "Reward"
    content: str       # raw value from request
    supported: bool
    detail: str        # ✅ detail or flag reason
    po_question: str = ""   # only set when not supported


@dataclass
class ReviewResult:
    campaign_name: str
    supported: list[ReviewPoint] = field(default_factory=list)
    needs_confirm: list[ReviewPoint] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.supported) + len(self.needs_confirm)


# ── Core review logic ─────────────────────────────────────────────────────────

def review_request(filepath: str) -> ReviewResult:
    """
    Parse the request file and check all points against KB allowlist.

    Returns a ReviewResult with supported and needs_confirm lists.
    """
    allowlist = load_allowlist()
    request = parse_request(filepath)

    result = ReviewResult(campaign_name=request["campaign_name"])

    game_types_kb = [_norm(g) for g in allowlist["scheme_game_type"]]
    trigger_map: dict[str, list[str]] = {
        t: [_norm(kw) for kw in kws]
        for t, kws in allowlist["task_trigger"].items()
    }
    reward_types_kb = [_norm(r) for r in allowlist["reward_type"]]

    # ── SCHEME — Game Type ────────────────────────────────────────────────────
    game_type_raw = request["game_type"]
    game_type_norm = _norm(game_type_raw)
    if game_type_norm in game_types_kb:
        result.supported.append(
            ReviewPoint(
                category="SCHEME",
                label="Game Type",
                content=game_type_raw,
                supported=True,
                detail='✅',
            )
        )
    else:
        result.needs_confirm.append(
            ReviewPoint(
                category="SCHEME",
                label="Game Type",
                content=game_type_raw,
                supported=False,
                detail="Không có trong KB allowlist",
                po_question=f'Game Type "{game_type_raw}" này đã available trên tool chưa?',
            )
        )

    # ── TASK — Trigger type ───────────────────────────────────────────────────
    for task in request["tasks"]:
        name = task["name"]
        desc = task["description"]
        trigger, kw = _find_trigger(name, desc, trigger_map)

        if trigger:
            result.supported.append(
                ReviewPoint(
                    category="TASK",
                    label=f'Task "{name}"',
                    content=f'{name}: {desc}' if desc else name,
                    supported=True,
                    detail=f'→ trigger = {trigger} ✅',
                )
            )
        else:
            result.needs_confirm.append(
                ReviewPoint(
                    category="TASK",
                    label=f'Task "{name}"',
                    content=f'tên task "{name}"' + (f', description "{desc}"' if desc else ""),
                    supported=False,
                    detail="Không xác định được trigger — không khớp keyword nào",
                    po_question=f'Trigger cho task "{name}" này đã available trên tool chưa?',
                )
            )

    # ── REWARD — Loại quà ────────────────────────────────────────────────────
    for reward in request["rewards"]:
        rtype = reward["type"]
        rdesc = reward["description"]
        rtype_norm = _norm(rtype)

        # Check if reward type matches any KB entry
        matched = None
        for kb_r in reward_types_kb:
            if kb_r in rtype_norm or rtype_norm in kb_r:
                matched = kb_r
                break

        if matched:
            result.supported.append(
                ReviewPoint(
                    category="REWARD",
                    label="Reward",
                    content=f"{rtype}" + (f" — {rdesc}" if rdesc else ""),
                    supported=True,
                    detail=f'→ {matched} ✅',
                )
            )
        else:
            result.needs_confirm.append(
                ReviewPoint(
                    category="REWARD",
                    label=f'Reward "{rtype}"',
                    content=f'loại quà = "{rtype}"' + (f' ({rdesc})' if rdesc else ""),
                    supported=False,
                    detail="Không có trong KB allowlist",
                    po_question=f'Loại quà "{rtype}" đã available trên tool chưa? Map vào loại nào trong: voucher / xu / cashback / merchant code?',
                )
            )

    return result


# ── Formatter ─────────────────────────────────────────────────────────────────

def format_review(result: ReviewResult) -> str:
    lines = []
    lines.append(f"=== REVIEW: {result.campaign_name} ===")
    lines.append(
        f"Tổng point: {result.total} | Đã hỗ trợ: {len(result.supported)} | Cần confirm: {len(result.needs_confirm)}"
    )
    lines.append("")

    lines.append("--- ĐÃ HỖ TRỢ ---")
    if result.supported:
        for p in result.supported:
            lines.append(f"[{p.category}] {p.label} = {p.content} {p.detail}")
    else:
        lines.append("(không có)")
    lines.append("")

    lines.append("--- CẦN PO CONFIRM ---")
    if result.needs_confirm:
        for i, p in enumerate(result.needs_confirm, 1):
            lines.append(f"{i}. [{p.category}] {p.label}")
            lines.append(f"   Nội dung: {p.content}")
            lines.append(f"   Lý do: {p.detail}")
            lines.append(f"   Cần PO confirm: {p.po_question}")
            lines.append("")
    else:
        lines.append("(không có — tất cả point đã hỗ trợ)")

    return "\n".join(lines)
