"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

-> Dùng Jina hoặc self host hoặc bất cứ công cụ nào bạn quen
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    # TODO: Implement RRF.
    #
    # scores = {}
    # items = {}
    # for ranked_list in ranked_lists:
    #     for rank, item in enumerate(ranked_list, 1):
    #         item_id = item["id"]
    #         scores[item_id] = scores.get(item_id, 0.0) + 1 / (k + rank)
    #         items[item_id] = item
    #
    # ranked_ids = sorted(scores, key=scores.get, reverse=True)
    # results = []
    # for item_id in ranked_ids[:top_k]:
    #     result = items[item_id].copy()
    #     result["score"] = scores[item_id]
    #     result["retrieval_method"] = "hybrid"
    #     results.append(result)
    # return results
    scores, items = {}, {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0.0) + 1 / (k + rank)
            items[item_id] = item
    ranked_ids = sorted(scores, key=lambda item_id: (-scores[item_id], item_id))[:max(top_k, 0)]
    return [{**items[item_id], "score": scores[item_id], "retrieval_method": "hybrid"}
            for item_id in ranked_ids]


if __name__ == "__main__":
    dense = [{"id": "demo-1", "score": 0.9}, {"id": "demo-2", "score": 0.8}]
    bm25 = [{"id": "demo-2", "score": 4.0}, {"id": "demo-3", "score": 3.0}]
    for result in rerank_rrf([dense, bm25], top_k=3):
        print(result)
