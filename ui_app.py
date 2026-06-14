"""
Product Ops Campaign Agent — Local Demo UI (MVP 3)

Run:
    streamlit run ui_app.py

Three tabs:
    UC1 — Review Campaign Request
    UC2 — Setup Guide Q&A
    UC3 — Generate Ticket Content
"""

import sys
from pathlib import Path

import streamlit as st

# ── Make sure src/ is importable when launched from any working directory ──
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

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

# ── Sample file discovery ──────────────────────────────────────────────────
_SAMPLES_DIR = _ROOT / "data" / "samples"


def _list_samples() -> list[Path]:
    if not _SAMPLES_DIR.exists():
        return []
    return sorted(_SAMPLES_DIR.glob("*.md"))


# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["📋 UC1 · Review Campaign Request",
     "📖 UC2 · Setup Guide Q&A",
     "🎫 UC3 · Generate Ticket Content"]
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
        selected_path_uc1 = _SAMPLES_DIR / selected_name_uc1

        if st.button("▶ Run Review", key="uc1_run"):
            try:
                from src.review.reviewer import review_request, format_review
                result = review_request(str(selected_path_uc1))
                output = format_review(result)
                st.success("Review completed.")
                st.code(output, language="text")
            except FileNotFoundError as exc:
                st.error(f"File not found: {exc}")
            except ValueError as exc:
                st.error(f"Cannot parse request — {exc}")
            except Exception as exc:
                st.error(f"Unexpected error — please check the request file format. ({type(exc).__name__})")

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
                from src.setup_guide.rag import answer_question
                answer = answer_question(question.strip())
                st.success("Answer found.")
                st.code(answer, language="text")
            except FileNotFoundError as exc:
                st.error(f"KB file not found: {exc}")
            except Exception as exc:
                st.error(f"Unexpected error — ({type(exc).__name__})")

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
        selected_path_uc3 = _SAMPLES_DIR / selected_name_uc3

        if st.button("▶ Generate Ticket Content", key="uc3_run"):
            try:
                from src.draft_confirmation.generator import generate_draft
                draft = generate_draft(str(selected_path_uc3))
                output = draft.render()

                st.success("Ticket content generated.")
                st.code(output, language="text")

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
                st.error(f"Unexpected error — please check the request file format. ({type(exc).__name__})")
