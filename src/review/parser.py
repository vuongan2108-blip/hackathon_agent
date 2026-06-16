"""Parse a campaign request markdown file into structured data."""

from __future__ import annotations

import re
from pathlib import Path


def _parse_table_rows(text: str) -> list[list[str]]:
    """Extract rows from a markdown table, skip header/separator rows."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip separator rows (---|--- style)
        if re.match(r"^\|[\s\-|]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def parse_request(filepath: str | Path) -> dict:
    """
    Parse a campaign request markdown file.

    Expected format:
      # Campaign Request — <name>
      | Field | Value |  (key-value table)
      ## Tasks
      | # | Task Name | Description |
      ## Rewards
      | # | Reward Type | Description |

    Returns:
        {
          "campaign_name": str,
          "game_type": str,
          "tasks": [{"name": str, "description": str}, ...],
          "rewards": [{"type": str, "description": str}, ...],
        }

    Raises:
        ValueError: if the file cannot be parsed.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Request file not found: {filepath}")

    content = path.read_text(encoding="utf-8")

    # ── Campaign name from h1 heading ───────────────────────────────────────
    h1_match = re.search(r"^#\s+Campaign Request\s*[—-]\s*(.+)$", content, re.MULTILINE)
    if not h1_match:
        raise ValueError("Missing '# Campaign Request — <name>' heading.")
    campaign_name = h1_match.group(1).strip()

    # ── Split into sections ─────────────────────────────────────────────────
    # Find h2 headings
    section_pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    headings = list(section_pattern.finditer(content))

    # Everything before first h2 = general info table
    general_end = headings[0].start() if headings else len(content)
    general_block = content[h1_match.end():general_end]

    # Parse key-value table for general fields
    general_data: dict[str, str] = {}
    for row in _parse_table_rows(general_block):
        if len(row) >= 2:
            general_data[row[0].lower()] = row[1]

    game_type = general_data.get("game type", "").strip()
    if not game_type:
        raise ValueError("'Game Type' field not found in request.")

    # ── Tasks section ────────────────────────────────────────────────────────
    tasks: list[dict] = []
    task_section = _get_section(content, headings, "Tasks")
    if task_section:
        for row in _parse_table_rows(task_section):
            if len(row) >= 2 and not row[0].startswith("#"):
                # row[0]=index, row[1]=name, row[2]=description (optional)
                name = row[1] if len(row) > 1 else ""
                description = row[2] if len(row) > 2 else ""
                if name:
                    tasks.append({"name": name, "description": description})

    # ── Rewards section ──────────────────────────────────────────────────────
    rewards: list[dict] = []
    reward_section = _get_section(content, headings, "Rewards")
    if reward_section:
        for row in _parse_table_rows(reward_section):
            if len(row) >= 2 and not row[0].startswith("#"):
                rtype = row[1] if len(row) > 1 else ""
                desc = row[2] if len(row) > 2 else ""
                if rtype:
                    rewards.append({"type": rtype, "description": desc})

    if not tasks and not rewards:
        raise ValueError("No tasks or rewards found — check request file format.")

    # ── Go-live date (Thời gian diễn ra) ────────────────────────────────────
    go_live_date = (
        general_data.get("thời gian diễn ra", "").strip()
        or general_data.get("thoi gian dien ra", "").strip()
    )

    # ── General fields (raw, lowercased keys) ────────────────────────────────
    general_fields = general_data  # expose for template checks

    # ── Game UI section ──────────────────────────────────────────────────────
    game_ui: dict[str, str] = {}
    game_ui_section = _get_section(content, headings, "Game UI")
    if game_ui_section:
        for row in _parse_table_rows(game_ui_section):
            if len(row) >= 2 and not row[0].startswith("#"):
                # Skip the header row (Field / Value)
                if row[0].lower().strip() == "field" and row[1].lower().strip() == "value":
                    continue
                game_ui[row[0].strip()] = row[1].strip()

    return {
        "campaign_name": campaign_name,
        "game_type": game_type,
        "tasks": tasks,
        "rewards": rewards,
        "go_live_date": go_live_date,
        "general_fields": general_fields,
        "game_ui": game_ui,
    }


def _get_section(content: str, headings: list, section_name: str) -> str | None:
    """Return the text body of the section matching section_name."""
    for i, heading in enumerate(headings):
        if heading.group(1).strip().lower() == section_name.lower():
            start = heading.end()
            end = headings[i + 1].start() if i + 1 < len(headings) else len(content)
            return content[start:end]
    return None
