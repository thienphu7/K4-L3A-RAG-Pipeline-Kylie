"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation. Nếu thiếu evidence, hãy từ chối xác minh."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context."""
    # TODO: Implement document reordering.
    #
    # if len(chunks) <= 2:
    #     return list(chunks)
    # front = chunks[::2]
    # back = chunks[1::2]
    # return front + back[::-1]
    if len(chunks) <= 2:
        return list(chunks)
    front = list(chunks[::2])
    back = list(chunks[1::2])
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    # TODO: Format chunks để LLM tạo citation kiểm chứng được.
    #
    # parts = []
    # for index, chunk in enumerate(chunks, 1):
    #     metadata = chunk["metadata"]
    #     parts.append(
    #         f"[Document {index} | Title: {metadata['title']} | "
    #         f"Source: {metadata['source']}]\n{chunk['content']}"
    #     )
    # return "\n\n---\n\n".join(parts)
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(f"[Document {index} | Title: {metadata['title']} | Source: {metadata['source']}]\n"
                     f"{chunk['content']}")
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    # TODO: Dispatch theo LLM_PROVIDER.
    #
    # - openai    -> OPENAI_API_KEY
    # - gemini    -> GEMINI_API_KEY
    # - anthropic -> ANTHROPIC_API_KEY
    #
    # Dùng LLM_MODEL và trả về text thuần cho cả ba nhánh.
    provider = LLM_PROVIDER.lower()
    if provider == "openai":
        from openai import OpenAI
        response = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).chat.completions.create(
            model=LLM_MODEL or "gpt-4o-mini", temperature=TEMPERATURE, top_p=TOP_P,
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_message}],
        )
        return response.choices[0].message.content or ""
    if provider == "gemini":
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(model=LLM_MODEL or "gemini-2.0-flash",
                                                  contents=f"{system_prompt}\n\n{user_message}")
        return response.text or ""
    if provider == "anthropic":
        from anthropic import Anthropic
        response = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")).messages.create(
            model=LLM_MODEL or "claude-3-5-haiku-latest", max_tokens=1200,
            system=system_prompt, messages=[{"role": "user", "content": user_message}],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    # TODO: Implement end-to-end generation.
    #
    # chunks = retrieve(query, top_k=top_k)
    # if not chunks:
    #     return {
    #         "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
    #         "sources": [],
    #         "retrieval_source": "none",
    #     }
    # reordered = reorder_for_llm(chunks)
    # context = format_context(reordered)
    # user_message = f"Context:\n{context}\n\nQuestion: {query}"
    # answer = call_llm(SYSTEM_PROMPT, user_message)
    # return {
    #     "answer": answer,
    #     "sources": chunks,
    #     "retrieval_source": chunks[0]["retrieval_method"],
    # }
    refusal = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {"answer": refusal, "sources": [], "retrieval_source": "none"}
    try:
        answer = call_llm(SYSTEM_PROMPT, f"Context:\n{format_context(reorder_for_llm(chunks))}\n\nQuestion: {query}")
    except Exception:
        answer = refusal
    source = chunks[0].get("retrieval_method")
    retrieval_source = source if source in {"hybrid", "pageindex"} else "hybrid"
    return {"answer": answer.strip() or refusal, "sources": chunks,
            "retrieval_source": retrieval_source}


if __name__ == "__main__":
    print(generate_with_citation("test query"))
