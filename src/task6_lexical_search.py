"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from .task4_chunking_indexing import chunk_documents, load_documents


CORPUS: list[dict] = []


def _expand_query(query: str) -> list[str]:
    """Add domain synonyms used by legal documents for everyday wording."""
    normalized = query.lower()
    terms = [normalized]
    if "vượt đèn đỏ" in normalized or "vượt đèn" in normalized:
        terms.append("không chấp hành hiệu lệnh đèn tín hiệu giao thông")
    if "xe máy" in normalized:
        terms.append("xe mô tô xe gắn máy")
    return " ".join(terms).split()


def _get_corpus() -> list[dict]:
    """Load the same chunks as indexing when no corpus was injected."""
    global CORPUS
    if not CORPUS:
        CORPUS = chunk_documents(load_documents())
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    # TODO: Tokenize và tạo BM25 index.
    #
    # from rank_bm25 import BM25Okapi
    # tokenized = [item["content"].lower().split() for item in corpus]
    # return BM25Okapi(tokenized)
    from rank_bm25 import BM25Okapi
    return BM25Okapi([item["content"].lower().split() for item in corpus])


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    # TODO: Tính BM25 scores và map lại corpus.
    #
    # import numpy as np
    # bm25 = build_bm25_index(CORPUS)
    # scores = bm25.get_scores(query.lower().split())
    # indices = np.argsort(scores)[::-1][:top_k]
    # results = []
    # for index in indices:
    #     if scores[index] <= 0:
    #         continue
    #     item = CORPUS[index]
    #     results.append({
    #         "id": item["id"],
    #         "content": item["content"],
    #         "score": float(scores[index]),
    #         "metadata": item["metadata"],
    #         "retrieval_method": "bm25",
    #     })
    # return results
    corpus = _get_corpus()
    if top_k <= 0 or not corpus:
        return []
    query_tokens = _expand_query(query)
    scores = build_bm25_index(corpus).get_scores(query_tokens)
    ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
    results = []
    for i, score in ranked[:top_k]:
        # BM25 can legitimately return 0 when a query term appears in half of
        # a tiny corpus (its IDF is then zero). Preserve lexical matches while
        # still excluding documents with no query-token overlap.
        tokens = set(corpus[i]["content"].lower().split())
        if not tokens.intersection(query_tokens):
            continue
        results.append({"id": corpus[i]["id"], "content": corpus[i]["content"],
                        "score": float(score), "metadata": corpus[i]["metadata"],
                        "retrieval_method": "bm25"})
    return results


if __name__ == "__main__":
    for result in lexical_search("phạt nguội", top_k=3):
        print(result)
