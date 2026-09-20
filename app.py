from __future__ import annotations

import os
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.demo_config import DEMO_PROMPTS, DOMAIN_DESCRIPTION, DOMAIN_NAME, WORKFLOW_STAGES
from src.task4_chunking_indexing import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CHUNKING_METHOD,
    EMBEDDING_MODEL,
)
from src.task9_retrieval_pipeline import SCORE_THRESHOLD
from src.task10_generation import LLM_MODEL, LLM_PROVIDER, generate_with_citation


load_dotenv()

ROOT = Path(__file__).parent
STANDARDIZED_DIR = ROOT / "data" / "standardized"

st.set_page_config(
    page_title="RoadSafe RAG · Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1500px;}
    [data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.2);}
    .domain-card {padding: 1rem; border-radius: .8rem; background: rgba(46, 134, 222, .10);
                  border: 1px solid rgba(46, 134, 222, .25); margin-bottom: 1rem;}
    .workflow-card {padding: .8rem; min-height: 118px; border-radius: .75rem;
                    border: 1px solid rgba(128,128,128,.22);}
    .workflow-number {font-size: .78rem; opacity: .7; text-transform: uppercase;}
    div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.18); padding: .7rem;
                                 border-radius: .7rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def corpus_stats() -> tuple[int, int]:
    legal = len(list((STANDARDIZED_DIR / "legal").glob("*.md")))
    news = len(list((STANDARDIZED_DIR / "news").glob("*.md")))
    return legal, news


def effective_embedding_model() -> str:
    return os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)


def effective_llm_model() -> str:
    defaults = {
        "openai": "gpt-4o-mini",
        "gemini": "gemini-2.0-flash",
        "anthropic": "claude-3-5-haiku-latest",
    }
    return LLM_MODEL or defaults.get(LLM_PROVIDER.lower(), "chưa cấu hình")


def score_label(source: dict) -> str:
    method = source.get("retrieval_method", "unknown")
    return "RRF" if method == "hybrid" else method.capitalize()


def render_sources(sources: list[dict]) -> None:
    if not sources:
        st.info("Không có đoạn tài liệu nào được dùng làm bằng chứng.")
        return

    st.markdown("#### Evidence được đưa vào LLM")
    st.caption(
        "RRF score là điểm hợp nhất thứ hạng, không phải phần trăm tin cậy. "
        "Với k=60, hạng 1 trong một danh sách có score xấp xỉ 0,0164."
    )
    for rank, source in enumerate(sources, 1):
        metadata = source.get("metadata", {})
        title = metadata.get("title") or metadata.get("source") or "Không rõ nguồn"
        method = source.get("retrieval_method", "unknown")
        score = float(source.get("score", 0.0))
        with st.expander(
            f"#{rank} · {title} · {score_label(source)} score={score:.4f}",
            expanded=rank == 1,
        ):
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Retriever", method)
            col_b.metric("Chunk", metadata.get("chunk_index", "—"))
            col_c.metric("Score", f"{score:.4f}")
            st.caption(f"Tệp nguồn: {metadata.get('source', 'Không rõ')}")
            st.code(source.get("content", ""), language=None)


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            metadata = message.get("run_metadata", {})
            if metadata:
                st.caption(
                    f"Retrieval: {metadata.get('retrieval_source', 'none')} · "
                    f"Top-k: {metadata.get('top_k', '—')} · "
                    f"Thời gian: {metadata.get('latency', 0):.2f}s"
                )
            render_sources(message.get("sources", []))


if "messages" not in st.session_state:
    st.session_state.messages = []

legal_count, news_count = corpus_stats()

with st.sidebar:
    st.title("⚖️ RoadSafe RAG")
    st.caption("Legal-domain retrieval augmented generation")
    st.markdown(
        f'<div class="domain-card"><strong>Domain</strong><br>{DOMAIN_NAME}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Phạm vi corpus**")
    st.write(f"{legal_count} văn bản pháp luật · {news_count} bài viết pháp luật")
    st.caption("Câu trả lời chỉ dựa trên dữ liệu đã thu thập, không thay thế tư vấn pháp lý.")

    st.divider()
    st.markdown("**Điều khiển truy xuất**")
    top_k = st.slider(
        "Số chunks đưa vào LLM",
        3,
        10,
        5,
        help="Top-k lớn tăng recall nhưng có thể làm context nhiều nhiễu hơn.",
    )
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("**Cấu hình đang chạy**")
    st.code(
        f"""LLM        {LLM_PROVIDER} / {effective_llm_model()}
Embedding  {os.getenv('EMBEDDING_PROVIDER', 'local')} / {effective_embedding_model()}
Chunking   {CHUNKING_METHOD} ({CHUNK_SIZE}, overlap {CHUNK_OVERLAP})
Vector DB  ChromaDB / cosine
Retrieval  Dense + BM25 + RRF (k=60)
Fallback   PageIndex khi dense < {SCORE_THRESHOLD}""",
        language=None,
    )

st.title("Trợ lý pháp luật giao thông đường bộ")
st.caption(DOMAIN_DESCRIPTION)

chat_tab, workflow_tab, prompts_tab = st.tabs(
    ["💬 Demo hội thoại", "🧭 Pipeline & mô hình", "🧪 Kịch bản kiểm thử"]
)

selected_prompt: str | None = None

with workflow_tab:
    st.subheader("Workflow end-to-end")
    workflow_columns = st.columns(3)
    for index, (number, title, description) in enumerate(WORKFLOW_STAGES):
        with workflow_columns[index % 3]:
            st.markdown(
                f'<div class="workflow-card"><div class="workflow-number">Bước {number}</div>'
                f'<strong>{title}</strong><br><span>{description}</span></div>',
                unsafe_allow_html=True,
            )
            st.write("")

    st.subheader("Vì sao nhóm chọn cấu hình này?")
    choices = [
        ("Embedding", effective_embedding_model(), "Tìm tương đồng ngữ nghĩa trong câu hỏi tiếng Việt."),
        ("Lexical", "BM25", "Giữ khả năng tìm số hiệu, điều khoản và cụm từ chính xác."),
        ("Fusion", "RRF, k=60", "Hợp nhất thứ hạng mà không cộng trực tiếp hai thang điểm khác nhau."),
        ("Chunking", f"{CHUNK_SIZE}/{CHUNK_OVERLAP}", "Cân bằng độ đầy đủ của điều khoản và kích thước context."),
        ("Generation", effective_llm_model(), "Sinh câu trả lời có grounding và safe refusal khi thiếu evidence."),
        ("Vectorless fallback", "PageIndex", "Thử cấu trúc tài liệu khi dense retrieval có độ tương đồng thấp."),
    ]
    for title, value, reason in choices:
        with st.expander(f"{title}: {value}"):
            st.write(reason)

    st.info(
        "Điểm hiển thị sau hybrid retrieval là RRF score. Nó đo sự đồng thuận về thứ hạng, "
        "không phải xác suất câu trả lời đúng."
    )

with prompts_tab:
    st.subheader("Prompt một-click cho buổi demo")
    st.write(
        "Bộ kịch bản bao gồm cả happy path, truy vấn khó và negative/adversarial cases. "
        "Nhấn **Chạy prompt** để gửi thẳng sang chatbot."
    )
    for index, item in enumerate(DEMO_PROMPTS):
        icon = {"success": "✅", "warning": "⚠️", "error": "🛡️"}[item["tone"]]
        with st.expander(f"{icon} {item['category']} · {item['label']}"):
            st.markdown(f"**Prompt:** {item['prompt']}")
            st.caption(f"Hành vi mong đợi: {item['expectation']}")
            if st.button("▶ Chạy prompt", key=f"demo-prompt-{index}"):
                selected_prompt = item["prompt"]

with chat_tab:
    if not st.session_state.messages:
        st.info(
            "Hãy nhập câu hỏi hoặc chọn một kịch bản trong tab **Kịch bản kiểm thử**. "
            "Sau mỗi câu trả lời, mở Evidence để kiểm tra chunk và nguồn thực tế."
        )
    st.caption("Chạy nhanh một kịch bản tiêu biểu")
    quick_prompt_indexes = [0, 1, 3, 5, 6]
    quick_columns = st.columns(len(quick_prompt_indexes))
    for column, prompt_index in zip(quick_columns, quick_prompt_indexes):
        item = DEMO_PROMPTS[prompt_index]
        if column.button(item["label"], key=f"quick-prompt-{prompt_index}", use_container_width=True):
            selected_prompt = item["prompt"]
    for message in st.session_state.messages:
        render_message(message)

typed_query = st.chat_input("Hỏi về luật, nghị định và an toàn giao thông đường bộ…")
query = selected_prompt or typed_query

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with chat_tab:
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            started = time.perf_counter()
            with st.spinner("Đang truy xuất, hợp nhất kết quả và kiểm tra evidence…"):
                result = generate_with_citation(query, top_k=top_k)
            latency = time.perf_counter() - started
            answer = result["answer"]
            sources = result["sources"]
            st.markdown(answer)
            st.caption(
                f"Retrieval: {result['retrieval_source']} · Top-k: {top_k} · "
                f"Thời gian: {latency:.2f}s"
            )
            render_sources(sources)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "run_metadata": {
                "retrieval_source": result["retrieval_source"],
                "top_k": top_k,
                "latency": latency,
            },
        }
    )
