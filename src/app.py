"""
Product Ops Campaign Agent — CLI entry point.

Usage:
    python -m src.app review <request_file>
    python -m src.app ask "<question>"
    python -m src.app draft-confirmation <request_file>
    python -m src.app generate-ticket-content <request_file>
    python -m src.app timeline <request_file>
"""

import sys
from typing import Optional


def cmd_review(args: list[str]) -> int:
    if not args:
        print("Usage: python -m src.app review <request_file>", file=sys.stderr)
        return 1

    filepath = args[0]
    try:
        from src.review.reviewer import review_request, format_review
        result = review_request(filepath)
        print(format_review(result))
        return 0
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"[ERROR] Cannot parse request: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


def _run_draft(filepath: str, save_to: Optional[str] = None) -> int:
    """Shared logic for draft-confirmation and generate-ticket-content."""
    try:
        from src.draft_confirmation.generator import generate_draft
        import pathlib
        result = generate_draft(filepath)
        output = result.render()
        print(output)
        if save_to:
            out_path = pathlib.Path(save_to)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output, encoding="utf-8")
            print(f"\n[Saved → {save_to}]", file=sys.stderr)
        return 0
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"[ERROR] Cannot parse request: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


def cmd_draft_confirmation(args: list[str]) -> int:
    if not args:
        print(
            "Usage: python -m src.app draft-confirmation <request_file>",
            file=sys.stderr,
        )
        return 1
    return _run_draft(args[0])


def cmd_draft(args: list[str]) -> int:
    """draft: alias for draft-confirmation."""
    if not args:
        print(
            "Usage: python -m src.app draft <request_file>",
            file=sys.stderr,
        )
        return 1
    return _run_draft(args[0])


def cmd_generate_ticket_content(args: list[str]) -> int:
    """generate-ticket-content: same as draft-confirmation, also saves combined output file."""
    if not args:
        print(
            "Usage: python -m src.app generate-ticket-content <request_file>",
            file=sys.stderr,
        )
        return 1
    return _run_draft(
        args[0],
        save_to="demo_outputs/generate_ticket_content_output_sample.txt",
    )


def cmd_timeline(args: list[str]) -> int:
    """timeline: generate Gantt-style markdown timeline from a campaign request."""
    if not args:
        print(
            "Usage: python -m src.app timeline <request_file>",
            file=sys.stderr,
        )
        return 1
    filepath = args[0]
    try:
        from src.timeline.generator import generate_timeline
        import pathlib
        result = generate_timeline(filepath)
        output = result.render()
        print(output)
        save_to = "demo_outputs/timeline_output_sample.txt"
        out_path = pathlib.Path(save_to)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"\n[Saved → {save_to}]", file=sys.stderr)
        return 0
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"[ERROR] Cannot parse request: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


def cmd_ask(args: list[str]) -> int:
    if not args:
        print("Usage: python -m src.app ask \"<question>\"", file=sys.stderr)
        return 1

    question = " ".join(args)
    try:
        from src.setup_guide.rag import answer_question
        answer = answer_question(question)
        print(answer)
        return 0
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print(
            "Commands: review <file>  |  ask \"<question>\"  |  "
            "draft <file>  |  draft-confirmation <file>  |  "
            "generate-ticket-content <file>  |  timeline <file>"
        )
        return 0

    command = argv[0].lower()
    rest = argv[1:]

    if command == "review":
        return cmd_review(rest)
    elif command == "ask":
        return cmd_ask(rest)
    elif command in ("draft", "draft-confirmation"):
        return cmd_draft_confirmation(rest)
    elif command == "generate-ticket-content":
        return cmd_generate_ticket_content(rest)
    elif command == "timeline":
        return cmd_timeline(rest)
    else:
        print(
            f"Unknown command: {command}. "
            "Use 'review', 'ask', 'draft', 'draft-confirmation', "
            "'generate-ticket-content', or 'timeline'.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
