# Báo cáo cá nhân — DangQuangDuy-2A202603984

## 1. Thông tin thành viên

- Họ tên: Đặng Quang Duy
- MSSV: 2A202603984
- Email: 26ai.duydq2@vinuni.edu.vn
- Nhóm: Tuesday

## 2. Phần việc phụ trách

Trong nhóm Tuesday (Research Agent, model `qwen3:1.7b` qua Ollama-compatible API), mình phụ trách phần **đo lường và kiểm chứng**:

- Chạy baseline eval cho agent ở phiên bản v0.
- Viết bộ eval nhóm `starter_v0/data/eval_group.json` (10 case: 5 single turn + 5 multi turn).
- Viết unit test cho tool mới `doi_lookup` và test cho bộ chấm.
- Chạy chat live để thu transcript làm bằng chứng cho báo cáo nhóm (mục B4).

## 3. Đóng góp cụ thể

**Baseline.** Chạy baseline v0 với prompt và tool declaration gốc: case accuracy 0.25 (5/20 case), làm mốc so sánh cho các vòng tối ưu v1–v5 (run `starter_v0/runs/v0_B_base_ollama_20261110T174716342985.json`).

**Eval nhóm (10 case).** Viết các case kiểm tra routing tới tool mới `doi_lookup` (G01, G06), tra chính sách (G02, G07), tìm paper arXiv (G03), định dạng nguồn đã có (G04), yêu cầu ngoài phạm vi (G05), sửa đổi giữa hội thoại (G08, G09) và xác nhận trước khi gửi Telegram (G10). Run group v5 cho kết quả 8/10 PASS (single turn 4/5, multi turn 4/5), 0 provider error.

**Phát hiện lỗi của chính bộ eval.**
- G04 ban đầu chỉ kiểm tra tên tool `format` nên pass dù model không truyền `items`. Sau khi bổ sung kiểm tra tham số, case bắt được lỗi này (FAIL: thiếu `items`).
- Bộ chấm gây `TypeError` khi so sánh danh sách object trong `items`. Mình sửa `run_eval.py` và thêm regression test `tests/test_eval_scoring.py`.

**Unit test.** Thêm 3 unit test cho `doi_lookup` trong `starter_v0/tests/test_tools_todo.py`: phản hồi thành công (kiểm tra metadata và URL request), input sai kiểu không phát sinh HTTP, và HTTP 429 trả error dict. Nhánh lỗi HTTP là phần eval routing không đo được. Kết quả `python -m pytest -q`: 71 passed, 14 skipped, 0 failed.

**Chat live.** Chạy và lưu transcript v5 cho ba tình huống: tra DOI (đúng tool `doi_lookup`), yêu cầu thiếu URL (FAIL ranh giới: không gọi `clarify`) và gửi Telegram (model gọi `send` quá sớm, guard `needs_confirmation` của tool chặn nên không có tin nhắn nào được gửi). Trên PowerShell, CLI lỗi encoding khi in tiếng Việt/emoji; mình cấu hình stdout UTF-8 trong `chat.py` rồi chạy lại transcript hợp lệ.

**Nhận xét rút ra từ số liệu.** Qua v0→v5, case accuracy tăng 0.25 → 0.35 và tool routing 0.45 → 0.65, nhưng multiturn accuracy vẫn 0.1667 và các lỗi ranh giới (`send`, `clarify`) chưa được giải quyết với model 1.7B.

## 4. Bằng chứng

- File/commit/PR:
  - Commit: `064fe9c`, `b6e2a34`, `555c6ff`
  - Eval: `starter_v0/data/eval_group.json`, `starter_v0/runs/v5_B_group_ollama_20261110T184051667335.json`
  - Test: `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/test_eval_scoring.py`
  - Sửa bộ chấm / CLI: `starter_v0/run_eval.py`, `chat.py`
  - Run baseline: `starter_v0/runs/v0_B_base_ollama_20261110T174716342985.json`
  - Transcript live: `starter_v0/transcripts/v5_ollama_20261110T185614797492.transcript.json`, `starter_v0/transcripts/v5_ollama_20261110T185635413478.transcript.json`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Claude hỗ trợ soạn thảo báo cáo này từ báo cáo nhóm; mình đối chiếu từng con số và đường dẫn file với run JSON, transcript và commit thật trước khi nộp.
  - Với code/test: chạy lại `python -m pytest -q` và kiểm tra số pass/skip/fail; với eval: chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`; đọc `results[*].result.failures` trong run JSON thay vì chỉ nhìn điểm tổng.

## 5. Tự đánh giá

**Làm tốt:** Bám bằng chứng. Eval của nhóm không chỉ chấm tên tool mà còn chấm tham số, nhờ đó lộ ra lỗi G04 mà trước đó bị che; mình cũng sửa lỗi bộ chấm và để lại regression test. Mỗi kết luận trong báo cáo đều trỏ tới run hoặc transcript cụ thể.

**Hạn chế:**
- Eval chỉ chấm tool call và args, chưa đánh giá chất lượng câu trả lời cuối; unit test `doi_lookup` dùng HTTP mock nên chưa kiểm chứng API Crossref thật.
- Chỉ có một model local nên chưa đủ điều kiện bonus Small Local Model; chưa có bug thật trong tool có sẵn nên chưa đủ bonus Test challenge.
- Mới thử các thay đổi prompt/tool ở mức một lần chạy mỗi phiên bản, chưa lặp lại nhiều lần để đo độ dao động của model 1.7B.

**Nếu có thêm thời gian:** thêm ví dụ ngắn cạnh quy tắc `clarify`/`send` (giả thuyết của nhóm ở B6), chạy lại base và group với cùng model, rồi so sánh từng failure với v5; đồng thời thêm kiểm tra chất lượng câu trả lời sau tool call.
