# RAG evaluation results

## Run information

| Field | Value |
|---|---|
| Evaluation date | 2026-09-20 |
| Framework and version | RAGAS 0.4.3; pytest 9.1.1 |
| Evaluator model | `gpt-4o-mini` |
| Generator model | `gpt-4o-mini` |
| Embedding model | `text-embedding-3-small` |
| Corpus version/commit | `dfbba10`; 6 legal Markdown, 5 news Markdown, 1,834 chunks |
| Golden dataset size | 16 |
| `top_k` | 5 |
| Fallback threshold and calibration | `SCORE_THRESHOLD=0.3`; PageIndex chưa cấu hình, chưa có benchmark threshold riêng |

## Configurations

- **Config A — dense-only:** `retrieve(..., use_reranking=False)`.
- **Config B — hybrid + RRF:** `retrieve(..., use_reranking=True)`, kết hợp dense và BM25 bằng Reciprocal Rank Fusion.

Hai cấu hình dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy. Kết quả chi tiết từng câu nằm trong `benchmark_results.json` và có thể tái lập bằng `python group_project/evaluation/run_evaluation.py`.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
|---|---:|---:|---:|
| Faithfulness | 0.845 | **0.939** | +0.094 |
| Answer relevance | **0.566** | 0.557 | -0.009 |
| Context recall | 0.802 | **0.948** | +0.146 |
| Context precision | 0.823 | **0.837** | +0.014 |
| **Average** | 0.759 | **0.820** | **+0.061** |

Các giá trị là trung bình trên 16 câu. RAGAS cảnh báo metric Answer Relevance chỉ nhận một câu hỏi tái tạo thay vì ba; vì vậy metric này có độ ổn định thấp hơn ba metric còn lại.

## A/B comparison

- Cấu hình tốt hơn: **Config B — hybrid + RRF**.
- Evidence: điểm trung bình tăng 0.061; Faithfulness tăng 0.094; Context Recall tăng mạnh nhất, 0.146. Tài liệu kỳ vọng xuất hiện trong top-5 ở 16/16 câu cho cả hai cấu hình, nhưng hybrid chọn đúng chunk chứa câu trả lời tốt hơn ở các câu 7 và 13.
- Trade-off về latency/cost: Config A đo được trung bình 2.30 giây/câu và Config B 1.77 giây/câu trong lượt chạy này. Chênh lệch chủ yếu chịu ảnh hưởng độ trễ API và không chứng minh hybrid nhanh hơn; hybrid vẫn có thêm chi phí CPU cho BM25 và RRF.
- Nhận xét: hệ thống hoạt động khá tốt trên tập kiểm thử hiện tại, đặc biệt về grounding và recall khi dùng hybrid. Tuy nhiên, Answer Relevance chỉ khoảng 0.56 và vẫn có câu trả lời sai/thiếu, nên chưa nên xem là sẵn sàng cho tình huống pháp lý cần độ chính xác cao.

### Query normalization note

Một số câu hỏi dùng cách nói đời thường và cần được ánh xạ sang cách diễn đạt trong văn bản pháp luật. Ví dụ:

- Câu hỏi người dùng: **“Xe máy vượt đèn đỏ bị phạt bao nhiêu?”**
- Cách diễn đạt trong nguồn: **“Không chấp hành hiệu lệnh của đèn tín hiệu giao thông.”**

Pipeline bổ sung mở rộng từ khóa cho nhóm đồng nghĩa này để BM25 và hybrid retrieval tìm được điều khoản phù hợp hơn.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 | Nghị định 236/2026/NĐ-CP quy định gì về thiết bị phát tín hiệu của xe ưu tiên? | B | 0.667 | 0.000 | 1.000 | 0.679 | generation | Đúng nguồn đã được retrieve nhưng câu trả lời chỉ nói về mẫu giấy phép rồi tự nhận thiếu thông tin, chưa trả lời đầy đủ điều kiện lắp đặt/sử dụng. |
| 2 | Theo Nghị định 151/2024/NĐ-CP, cơ sở dữ liệu giao thông có thể gồm thông tin nào? | A | 0.500 | 0.680 | 0.333 | 0.478 | retrieval + generation | Chunk đúng nằm thấp; context bị lẫn tài liệu sửa đổi và câu trả lời chỉ nêu một nhóm thông tin. |
| 3 | Nghị định 238/2026/NĐ-CP có hiệu lực từ ngày nào? | A | 1.000 | 0.800 | 0.000 | 0.000 | retrieval | Retrieve đúng tên nguồn nhưng sai đoạn, khiến model trả lời sai `01/01/2028`; hybrid trả đúng `15/8/2026`. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
|---:|---|---|---|---|
| 1 | Dùng hybrid + RRF làm cấu hình mặc định | Average +0.061 và Context Recall +0.146 so với dense-only | Giảm bỏ sót evidence và lỗi trả lời do chọn sai chunk | Chạy lại cùng golden dataset và một tập holdout mới |
| 2 | Cải thiện chunking theo điều/khoản, thêm document number vào metadata/content | Câu 7, 13 và 16 lấy đúng tài liệu nhưng chưa chọn đúng đoạn | Tăng Context Precision và độ chính xác chi tiết pháp lý | Đo lại recall/precision theo từng câu sau re-index |
| 3 | Siết prompt tạo câu trả lời: phải trả lời trực tiếp, kiểm tra ngày/số liệu và từ chối khi context mâu thuẫn | Answer Relevance chỉ 0.557–0.566; câu 14 hybrid trả lời thiếu | Tăng relevance và giảm câu trả lời tự mâu thuẫn | Thêm assertions cho ngày, mức phạt và câu hỏi định nghĩa |
| 4 | Calibrate `SCORE_THRESHOLD` với cả query in-domain và out-of-domain | Threshold 0.3 chưa được kiểm chứng; PageIndex chưa cấu hình | Cải thiện safe refusal và giảm trả lời ngoài corpus | Đo ROC/precision-recall và fallback rate trên tập calibration |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
|---|---|---:|---:|---|
<<<<<<< HEAD
| OCR cho legal PDFs | Corpus chỉ có 1 legal Markdown | Chưa đo | Tăng thời gian tiền xử lý và embedding | Cần kiểm tra chất lượng OCR trước khi kết luận |
=======
| Hybrid + RRF | Dense-only | Average +0.061; recall +0.146 | Thêm BM25/RRF; latency API quan sát không ổn định | Có lợi rõ ràng, nên dùng làm mặc định |
| OCR cho legal PDFs | Corpus trước OCR chỉ có 1 legal Markdown | Chưa cô lập A/B riêng; corpus hiện có đủ 6 legal files | Tăng thời gian tiền xử lý/indexing | Cần giữ OCR nhưng nên làm sạch ký tự nhiễu trước khi chunking |
>>>>>>> 18a2bde (Update evaluation and result)
