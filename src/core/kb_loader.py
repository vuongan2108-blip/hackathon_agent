"""KB Loader — reads local KB files only. No external API calls."""

import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_KB_DIR = _ROOT / "data" / "kb"

_ALLOWLIST_FILE = _KB_DIR / "kb_campaign_available.md"
_SETUP_GUIDE_FILE = _KB_DIR / "kb_setup_guide_content_v1.md"


def load_allowlist() -> dict:
    """
    Parse kb_campaign_available.md and return the machine-readable JSON block.

    Returns:
        {
          "scheme_game_type": [...],
          "task_trigger": {"payment": [...], ...},
          "reward_type": [...],
          "rule": "..."
        }
    """
    if not _ALLOWLIST_FILE.exists():
        raise FileNotFoundError(f"KB allowlist not found: {_ALLOWLIST_FILE}")

    content = _ALLOWLIST_FILE.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if not match:
        raise ValueError("JSON block not found in KB allowlist file.")

    return json.loads(match.group(1))


def load_setup_guide_sections() -> list[dict]:
    """
    Parse kb_setup_guide_content_v1.md into sections.

    Each section is a dict:
        {
          "id": "A1",
          "title": "[SCHEME] Lucky Wheel",
          "source": "https://...",
          "aliases": [...],
          "content": "full text of section"
        }
    """
    if not _SETUP_GUIDE_FILE.exists():
        raise FileNotFoundError(f"Setup guide KB not found: {_SETUP_GUIDE_FILE}")

    raw = _SETUP_GUIDE_FILE.read_text(encoding="utf-8")

    # Split on level-2 headings (## Axx / ## Bxx / ## Cxx / ## PART)
    pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    headings = list(pattern.finditer(raw))

    sections = []
    for i, heading in enumerate(headings):
        title_full = heading.group(1).strip()
        start = heading.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(raw)
        body = raw[start:end].strip()

        # Skip structural dividers like "PART A — SCHEME PAGES"
        if title_full.startswith("PART "):
            continue

        # Extract section ID from title (e.g. "A1. [SCHEME] Lucky Wheel" → "A1")
        id_match = re.match(r"^([A-C]\d+)\.\s*(.*)", title_full)
        if id_match:
            section_id = id_match.group(1)
            section_title = id_match.group(2).strip()
        else:
            section_id = title_full[:4].strip(".")
            section_title = title_full

        # Extract source URL
        source_match = re.search(r"- source:\s*(https?://\S+)", body)
        source = source_match.group(1).rstrip(")") if source_match else ""

        # Extract aliases
        alias_match = re.search(r"- aliases:\s*\[([^\]]+)\]", body)
        aliases = []
        if alias_match:
            aliases = [a.strip() for a in alias_match.group(1).split(",")]

        sections.append(
            {
                "id": section_id,
                "title": section_title,
                "source": source,
                "aliases": aliases,
                "content": body,
            }
        )

    return sections
