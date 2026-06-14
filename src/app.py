"""
Product Ops Campaign Agent — CLI entry point.

Usage:
    python -m src.app review <request_file>
    python -m src.app ask "<question>"
"""

import sys


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
        print("Commands: review <file>  |  ask \"<question>\"")
        return 0

    command = argv[0].lower()
    rest = argv[1:]

    if command == "review":
        return cmd_review(rest)
    elif command == "ask":
        return cmd_ask(rest)
    else:
        print(f"Unknown command: {command}. Use 'review' or 'ask'.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
