# RAG evaluation results

## Run information

| Field | Value |
|---|---|
| Evaluation date | 2026-09-20 |
| Framework and version | pytest 9.1.1; RAGAS evaluator chưa chạy trong pass này |
| Evaluator model | Chưa chạy evaluator tự động |
| Generator model | Theo `LLM_MODEL` trong `.env` |
| Embedding model | Theo `EMBEDDING_MODEL` trong `.env` |
| Corpus version/commit | Working tree sau OCR; 6 legal Markdown và 5 news Markdown |
| Golden dataset size | 15 |
| `top_k` | 5 |
| Fallback threshold and calibration | `SCORE_THRESHOLD=0.3`; cần calibrate thêm bằng query thực tế |

## Configurations

- **Config A — dense-only:** Đã triển khai trong `retrieve(..., use_reranking=False)` nhưng chưa chạy benchmark tự động.
- **Config B — hybrid + RRF:** Đã triển khai trong `retrieve(..., use_reranking=True)`; contract tests pass.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
|---|---:|---:|---:|
| Faithfulness | N/A | N/A | N/A |
| Answer relevance | N/A | N/A | N/A |
| Context recall | N/A | N/A | N/A |
| Context precision | N/A | N/A | N/A |
| **Average** | N/A | N/A | N/A |

Các metric tự động chưa có số liệu vì chưa chạy evaluator trên cùng một generator/evaluator configuration. Không điền số giả.

## A/B comparison

- Cấu hình tốt hơn: Chưa kết luận trước khi chạy benchmark 15 câu.
- Evidence: Dense search, BM25 và RRF đã pass contract tests; chưa có điểm metric định lượng.
- Trade-off về latency/cost: Hybrid thực hiện dense và BM25 rồi fuse; dense-only ít bước hơn, hybrid tận dụng cả ngữ nghĩa và từ khóa chính xác.

### Query normalization note

Một số câu hỏi dùng cách nói đời thường và cần được ánh xạ sang cách diễn đạt trong văn bản pháp luật. Ví dụ:

- Câu hỏi người dùng: **“Xe máy vượt đèn đỏ bị phạt bao nhiêu?”**
- Cách diễn đạt trong nguồn: **“Không chấp hành hiệu lệnh của đèn tín hiệu giao thông.”**

Pipeline bổ sung mở rộng từ khóa cho nhóm đồng nghĩa này để BM25 và hybrid retrieval tìm được điều khoản phù hợp hơn.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Câu hỏi kiểm tra `test query` | Config B | N/A | N/A | N/A | N/A | retrieval | Query không thuộc corpus nên hệ thống safe refusal. |
| 2 | Câu hỏi về chi tiết OCR | Config B | N/A | N/A | N/A | N/A | data | Một số bảng PDF scan bị OCR nhiễu. |
| 3 | Câu hỏi chưa có trong corpus | Config A/B | N/A | N/A | N/A | N/A | retrieval | Không có evidence phù hợp; expected behavior là từ chối xác minh. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
|---:|---|---|---|---|
| 1 | Chạy benchmark 15 câu với cùng prompt/model cho dense-only và hybrid + RRF | Chưa có số liệu A/B | Có kết quả định lượng | Lưu output từng cấu hình và chạy evaluator |
| 2 | Làm sạch đoạn OCR nhiễu và loại chunk quá ngắn | Một số chunk chứa bảng/ký tự rác | Tăng context precision và citation quality | Re-index rồi kiểm tra các câu hỏi pháp lý |
| 3 | Calibrate `SCORE_THRESHOLD` bằng query in-domain và out-of-domain | Threshold hiện mới là giá trị mặc định | Giảm fallback sai và tăng safe refusal đúng lúc | Đo recall/fallback rate theo threshold |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
|---|---|---:|---:|---|
| OCR cho legal PDFs | Corpus chỉ có 1 legal Markdown | Chưa đo | Tăng thời gian tiền xử lý và embedding | Cần kiểm tra chất lượng OCR trước khi kết luận |

