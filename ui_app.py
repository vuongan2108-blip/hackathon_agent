"""
Product Ops Campaign Agent — Local Demo UI (MVP 3 + UC4)

Run:
    streamlit run ui_app.py

Four tabs:
    UC1 — Review Campaign Request
    UC2 — Setup Guide Q&A
    UC3 — Generate Ticket Content
    UC4 — Timeline Campaign Assistant
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

import streamlit as st

# ── Ensure repo root is on sys.path regardless of cwd ─────────────────────
# .resolve() makes this an absolute path on every OS (important on Windows).
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ── Sample file discovery ──────────────────────────────────────────────────
_SAMPLES_DIR = _ROOT / "data" / "samples"


def _list_samples() -> list[Path]:
    if not _SAMPLES_DIR.exists():
        return []
    return sorted(_SAMPLES_DIR.glob("*.md"))


# ── Wrapper functions — lazy imports, mirror CLI exactly ──────────────────
# Imports are deferred inside the function body so that any ImportError /
# TypeError from a module-level annotation is caught by the caller's
# try/except block, where traceback.format_exc() is still active.

def run_review_for_ui(sample_path: str) -> str:
    """Replicate `python -m src.app review <file>`. Returns display-ready text."""
    from src.review.reviewer import review_request, format_review  # noqa: PLC0415
    return format_review(review_request(sample_path))


def run_ask_for_ui(question: str) -> str:
    """Replicate `python -m src.app ask \"<question>\"`. Returns display-ready text."""
    from src.setup_guide.rag import answer_question  # noqa: PLC0415
    return answer_question(question)


def run_ticket_generation_for_ui(sample_path: str) -> str:
    """Replicate `python -m src.app generate-ticket-content <file>`. Returns display-ready text."""
    from src.draft_confirmation.generator import generate_draft  # noqa: PLC0415
    return generate_draft(sample_path).render()


def run_timeline_for_ui(sample_path: str) -> str:
    """Replicate `python -m src.app timeline <file>`. Returns display-ready text."""
    from src.timeline.generator import generate_timeline  # noqa: PLC0415
    return generate_timeline(sample_path).render()


# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Product Ops Campaign Agent",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Product Ops Campaign Agent — Local Demo")
st.caption(
    "Local file-based demo · No Jira · No Confluence · No external API calls · Mock data only"
)

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📋 UC1 · Review Campaign Request",
     "📖 UC2 · Setup Guide Q&A",
     "🎫 UC3 · Generate Ticket Content",
     "📅 UC4 · Timeline Campaign Assistant"]
)

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — UC1: Review Campaign Request
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("UC1 · Review Campaign Request")
    st.markdown(
        "Select a campaign request file. The agent checks Game Type, Task Triggers, "
        "and Reward Types against the local KB allowlist and splits the result into "
        "**ĐÃ HỖ TRỢ** (supported) and **CẦN PO CONFIRM** (needs confirmation)."
    )

    samples = _list_samples()
    if not samples:
        st.error("No sample files found in `data/samples/`. Check your repository structure.")
    else:
        sample_names = [p.name for p in samples]
        selected_name_uc1 = st.selectbox(
            "Campaign request file", sample_names, key="uc1_file"
        )
        # Convert to str immediately — no Path object passed to wrapper
        selected_path_uc1 = str(_SAMPLES_DIR / selected_name_uc1)

        if st.button("▶ Run Review", key="uc1_run"):
            try:
                output = run_review_for_ui(selected_path_uc1)
                st.success("Review completed.")
                st.code(output, language=None)
            except FileNotFoundError as exc:
                st.error(f"File not found: {exc}")
            except ValueError as exc:
                st.error(f"Cannot parse request — {exc}")
            except Exception as exc:
                # traceback.format_exc() is valid here — we are inside an active except block
                tb = traceback.format_exc()
                st.error(
                    f"Unexpected error — {type(exc).__name__}: {exc}"
                )
                with st.expander("Debug details"):
                    st.code(tb, language=None)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — UC2: Setup Guide Q&A
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("UC2 · Setup Guide Q&A")
    st.markdown(
        "Ask a natural-language question about campaign tool setup. "
        "The agent searches the local KB and returns the relevant steps plus "
        "the exact source section."
    )

    question = st.text_input(
        "Your question",
        placeholder='e.g. "cách setup Game Type lucky wheel"',
        key="uc2_question",
    )

    example_questions = [
        "cách setup Game Type lucky wheel",
        "cách setup task trigger payment",
        "tạo reward pool",
        "setup leaderboard",
    ]
    st.caption("Example questions: " + " · ".join(f'"{q}"' for q in example_questions))

    if st.button("▶ Ask", key="uc2_ask"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                answer = run_ask_for_ui(question.strip())
                st.success("Answer found.")
                st.code(answer, language=None)
            except FileNotFoundError as exc:
                st.error(f"KB file not found: {exc}")
            except Exception as exc:
                tb = traceback.format_exc()
                st.error(f"Unexpected error — {type(exc).__name__}: {exc}")
                with st.expander("Debug details"):
                    st.code(tb, language=None)

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — UC3: Generate Ticket Content
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("UC3 · Generate Ticket Content")
    st.markdown(
        "Select a campaign request file. The agent runs UC1 review internally, "
        "then drafts up to **4 coordination tickets** (Biz / Design / PO / Ops) "
        "with SLAs and dependencies."
    )
    st.info(
        "⚠️ **Ops phải review nội dung bên dưới trước khi copy-paste sang Jira.** "
        "Agent chỉ soạn nháp — KHÔNG ghi Jira tự động.",
        icon="⚠️",
    )

    samples_uc3 = _list_samples()
    if not samples_uc3:
        st.error("No sample files found in `data/samples/`.")
    else:
        sample_names_uc3 = [p.name for p in samples_uc3]
        selected_name_uc3 = st.selectbox(
            "Campaign request file", sample_names_uc3, key="uc3_file"
        )
        selected_path_uc3 = str(_SAMPLES_DIR / selected_name_uc3)

        if st.button("▶ Generate Ticket Content", key="uc3_run"):
            try:
                output = run_ticket_generation_for_ui(selected_path_uc3)
                st.success("Ticket content generated.")
                st.code(output, language=None)

                st.download_button(
                    label="⬇ Download as .txt (for Ops review & manual copy-paste to Jira)",
                    data=output.encode("utf-8"),
                    file_name=f"ticket_draft_{selected_name_uc3.replace('.md', '')}.txt",
                    mime="text/plain",
                    key="uc3_download",
                )

                st.caption(
                    "Ops: review xong thì copy từng ticket vào Jira. "
                    "Điền tên người/nhóm thật vào chỗ [assignee] trước khi gửi."
                )

            except FileNotFoundError as exc:
                st.error(f"File not found: {exc}")
            except ValueError as exc:
                st.error(f"Cannot parse request — {exc}")
            except Exception as exc:
                tb = traceback.format_exc()
                st.error(
                    f"Unexpected error — please check the request file format. "
                    f"{type(exc).__name__}: {exc}"
                )
                with st.expander("Debug details"):
                    st.code(tb, language=None)

# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — UC4: Timeline Campaign Assistant
# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("UC4 · Timeline Campaign Assistant")
    st.markdown(
        "Select a campaign request file. The agent runs UC3 internally, "
        "then generates a **Gantt-style markdown timeline** with 4 fixed actor rows "
        "and one column per calendar date from D0 (today) through T (go-live)."
    )
    st.info(
        "⚠️ **Ops: review timeline below. Nếu cần chỉnh sửa, chạy lại UC3 trước khi dùng.**",
        icon="⚠️",
    )

    samples_uc4 = _list_samples()
    if not samples_uc4:
        st.error("No sample files found in `data/samples/`.")
    else:
        sample_names_uc4 = [p.name for p in samples_uc4]
        selected_name_uc4 = st.selectbox(
            "Campaign request file", sample_names_uc4, key="uc4_file"
        )
        selected_path_uc4 = str(_SAMPLES_DIR / selected_name_uc4)

        if st.button("▶ Generate Timeline", key="uc4_run"):
            try:
                output = run_timeline_for_ui(selected_path_uc4)
                st.success("Timeline generated.")
                st.markdown(output)

                st.download_button(
                    label="⬇ Download as .txt (for Ops review)",
                    data=output.encode("utf-8"),
                    file_name=f"timeline_{selected_name_uc4.replace('.md', '')}.txt",
                    mime="text/plain",
                    key="uc4_download",
                )

            except FileNotFoundError as exc:
                st.error(f"File not found: {exc}")
            except ValueError as exc:
                st.error(f"Cannot parse request — {exc}")
            except Exception as exc:
                tb = traceback.format_exc()
                st.error(
                    f"Unexpected error — please check the request file format. "
                    f"{type(exc).__name__}: {exc}"
                )
                with st.expander("Debug details"):
                    st.code(tb, language=None)
