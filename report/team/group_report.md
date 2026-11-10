# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi agent với prompt và tool declaration gốc | — | 0.25 (5/20 case) | `starter_v0/runs/v0_B_base_ollama_20261110T174716342985.json` |
| v1 | `system_prompt.md` (quy tắc xác nhận trước `send`) | Quy tắc rõ ràng sẽ chuyển R12 từ `send` sang `clarify`; thực tế R12 vẫn FAIL | 0.25 | 0.20 (4/20 case) | `starter_v0/runs/v1_B_base_ollama_20261110T180802788870.json` |
| v2 | `tools.yaml` (chỉ description của `send`) | Mô tả điều kiện xác nhận tại tool sẽ chuyển R12 sang `clarify`; thực tế R12 vẫn FAIL | 0.20 | 0.10 (2/20 case) | `starter_v0/runs/v2_B_base_ollama_20261110T181246575962.json` |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R01_user_tweets_routing | wrong_tool (quan sát: wrong_arg_value) | `timeline(screenname="Sam Altman", limit=1)` | `screenname` cần là `sama`, không phải tên đầy đủ. | Mô tả quy tắc đổi tên người thành handle. |
| R03_web_news_routing | wrong_tool | `social_search(query="Tin tức AI hôm nay")` | Thiếu `lookup` cho tin web; gọi tìm mạng xã hội. | Phân biệt tin web với bài đăng mạng xã hội. |
| R05_limit_arg | wrong_arg_value (quan sát: sai tool) | `social_search(query="Elon Musk", limit=10)` | Cần `timeline(screenname="elonmusk", limit=10)`. | Ưu tiên `timeline` khi hỏi bài đăng của tài khoản cụ thể. |
| R06_timeframe_arg | wrong_arg_value (quan sát: sai tool) | `social_search(query="Tin công nghệ")` | Cần `lookup(topic="news", timeframe="week")`. | Nêu rõ quy tắc chọn `lookup` và ánh xạ khoảng thời gian. |
| R08_out_of_scope | out_of_scope | `lookup(query="integrate x^2")` | Bài toán tích phân ngoài phạm vi; kỳ vọng không gọi tool. | Thêm ranh giới phạm vi của research agent. |
| R10_missing_handle | missing_info | `social_search(query="tweet")` | Thiếu tài khoản nhưng agent tìm chung thay vì hỏi lại. | Gọi `clarify` khi chưa biết tài khoản cần xem. |
| R11_missing_url | missing_info | `lookup(query="Tóm tắt bài viết này")` | Không có URL bài viết nhưng agent tự tìm. | Gọi `clarify` để xin URL trước khi đọc bài. |
| R12_confirm_before_send | wrong_boundary | `send(text="Đăng bản tin này lên Telegram giúp mình")` | Gọi `send` trước khi người dùng xác nhận. | Bắt buộc `clarify(response_type="yes_no")` trước khi gửi. |
| R13_parallel_web_and_tweets | wrong_tool | `social_search(query="AI")` | Thiếu `lookup` cho phần tin web; chỉ tìm bài đăng. | Cho phép gọi cả `lookup` và `social_search` khi yêu cầu cả hai nguồn. |
| R14_out_of_scope_coding | out_of_scope | `lookup(query="Python Fibonacci recursion")` | Yêu cầu viết code ngoài phạm vi; kỳ vọng không gọi tool. | Nêu rõ các yêu cầu lập trình nằm ngoài phạm vi. |
| M01_clarify_then_fill | missing_info | `social_search(query="Elon Musk", limit=5)` | Sau khi có tên tài khoản vẫn không gọi `timeline(screenname="elonmusk")`. | Dùng thông tin bổ sung ở lượt sau và ánh xạ handle. |
| M02_carryover_timeframe | wrong_arg_value | `lookup(query="robotics", topic="general", timeframe="day")` | Giữ đúng `day` nhưng mất ngữ cảnh tin tức: cần `topic="news"`. | Giữ loại nguồn tin qua nhiều lượt. |
| M03_correction_handle | wrong_arg_value | `timeline(screenname="Sam Altman", limit=3)` | Không áp dụng sửa đổi tài khoản; cần `karpathy`. | Ưu tiên thông tin người dùng vừa sửa ở lượt cuối. |
| M05_correction_limit | wrong_arg_value | `timeline(screenname="elonmusk", limit=10)` | Không áp dụng số lượng mới; cần `limit=3`. | Lấy giới hạn mới nhất trong hội thoại. |
| M06_switch_tool | wrong_tool | `social_search(query="OpenAI")` | Người dùng chuyển sang tin web nhưng agent tiếp tục tìm mạng xã hội. | Chọn lại tool theo yêu cầu mới nhất mỗi lượt. |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
