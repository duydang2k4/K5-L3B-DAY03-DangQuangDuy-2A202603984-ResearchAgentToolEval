# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v5: Ollama-compatible API, `qwen3:1.7b`.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research Agent giúp tìm tin web và bài đăng X, đọc URL, tra paper/DOI, tìm chính sách nội bộ và tổng hợp thành bản tin. Với yêu cầu gửi Telegram, người dùng cần xác nhận trực tiếp trong UI; kết quả từ model nhỏ có thể chọn sai tool nên người thử nên xem phần “Tool calls & kết quả”.

**Cách chạy UI:**

Từ `starter_v0/`: `streamlit run app.py`. Dependency `streamlit` đã thêm vào `requirements.txt`; provider/model mặc định lấy từ `.env` (`ollama`, `OLLAMA_MODEL`).

**Link dùng thử (deploy):**

URL demo tạm thời: https://fuel-review-excess-control.trycloudflare.com (kiểm tra HTTP 200 ngày 10/11/2026). Link chỉ hoạt động khi Streamlit và Quick Tunnel trên máy demo còn chạy; khi khởi động lại tunnel cần cập nhật URL.

**Người trực demo:** Mai Danh Hiếu (giữ máy chạy Streamlit và Cloudflare Tunnel, hỗ trợ nhóm khác thử câu hỏi mới).

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy bài đăng gần đây của một tài khoản X | không |
| social_search | tìm bài đăng X theo chủ đề | không |
| lookup | tìm thông tin và tin tức trên web | không |
| fetch | đọc nội dung của một URL | không |
| format | định dạng các nguồn đã có thành digest | không |
| send | gửi Telegram sau xác nhận trong UI | không |
| policy | tra cứu chính sách nội bộ | không |
| papers | tìm paper trên arXiv | không |
| paper_text | đọc PDF arXiv đã xác định | không |
| doi_lookup | tra metadata bài báo theo DOI qua Crossref | có |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. `Tra tên bài, tác giả và năm xuất bản của DOI 10.1038/nphys1170.`
2. `Theo chính sách nội bộ, có được đưa dữ liệu cá nhân khách hàng vào AI bên ngoài không?`
3. `Tóm tắt bài viết này giúp mình.` (kiểm tra agent có hỏi URL hay không)
4. `Tìm 4 preprint arXiv mới nộp về retrieval augmented generation.`
5. `Đăng bản tin AI lên Telegram giúp mình.` (quan sát bước xác nhận trước khi gửi)

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
| v3 | `system_prompt.md` (chỉ đoạn xử lý thông tin thiếu) | Quy tắc hỏi khi thiếu dữ liệu sẽ cải thiện R10/R11; thực tế cả hai vẫn FAIL | 0.10 | 0.30 (6/20 case) | `starter_v0/runs/v3_B_base_ollama_20261110T181731243247.json` |
| v4 | `system_prompt.md` (bỏ ép một bước, một tool) | Cho phép nhiều tool sẽ xử lý yêu cầu đa nguồn; R13 vẫn FAIL | 0.30 | 0.30 (6/20 case) | `starter_v0/runs/v4_B_base_ollama_20261110T182735871967.json` |
| v5 | `tools.yaml` (mô tả cách dùng và args) | Khai báo rõ sẽ cải thiện routing/args; routing accuracy tăng 0.40 → 0.65 | 0.30 | 0.35 (7/20 case) | `starter_v0/runs/v5_B_base_ollama_20261110T183009801568.json` |

Giữa v3 và v4, nhóm đã thêm tool `doi_lookup` vào `tools.yaml`; vì vậy so sánh v3→v4 có thêm thay đổi ở tập tool. So sánh v4→v5 giữ nguyên prompt và danh sách tool, chỉ thay mô tả/arg convention.

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
| G01_lookup_exact_doi | DOI cụ thể route tới tool mới | `doi_lookup(doi="10.1038/nphys1170")` | PASS |
| G02_internal_privacy_policy | Chính sách dữ liệu cá nhân nội bộ | `policy(policy_area="data_privacy")` | PASS |
| G03_arxiv_recent_preprints | Tìm paper arXiv theo số lượng và ngày nộp | `papers(max_results=4, sort_by="submittedDate")` | PASS |
| G04_format_existing_sources | Định dạng đủ hai nguồn người dùng đã đưa | `format(template="bullets", items=[2 nguồn])` | FAIL: thiếu `items` |
| G05_translation_out_of_scope | Yêu cầu dịch thuật ngoài phạm vi | Không gọi tool | PASS |
| G06_doi_correction_multiturn | Dùng DOI được sửa ở lượt sau | `doi_lookup(doi="10.1145/3290605.3300233")` | PASS |
| G07_policy_area_switch_multiturn | Chuyển khu vực chính sách theo yêu cầu mới | `policy(policy_area="source_citation")` | PASS |
| G08_social_sort_correction_multiturn | Giữ chủ đề và đổi Latest → Top | `social_search(query="robotics", search_type="Top")` | PASS |
| G09_url_correction_multiturn | Chỉ đọc URL được sửa ở lượt sau | `fetch(url="https://en.wikipedia.org/wiki/Robotics")` | FAIL: gọi `format` với URL cũ |
| G10_send_requires_confirmation_multiturn | Xin xác nhận trước khi gửi Telegram | `clarify(response_type="yes_no")` | PASS |

Run group v5: `starter_v0/runs/v5_B_group_ollama_20261110T184051667335.json` — 10/10 case được đo, 0 provider error, 8/10 PASS; single turn 4/5, multi turn 4/5. Eval chấm tool call và args, không chứng minh output của API luôn đúng. Ví dụ G04 ban đầu chỉ kiểm tra tên tool nên pass dù thiếu `items`; sau khi bổ sung args cần kiểm tra, case bắt được lỗi này. Unit test `doi_lookup` còn kiểm tra HTTP 429 trả error dict, điều mà eval routing không đo.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `Look up metadata for DOI 10.1038/nphys1170.` | `doi_lookup` | `starter_v0/transcripts/v5_ollama_20261110T185614797492.transcript.json` (v5) | Tra metadata Crossref và trả lời có URL nguồn. |
| 2 | `Summarize an article for me. I have not provided its title or URL yet.` | Không gọi tool | `starter_v0/transcripts/v5_ollama_20261110T185635413478.transcript.json` (v5) | FAIL ranh giới: agent nói cần làm rõ nhưng không gọi `clarify` hoặc đặt câu hỏi trực tiếp. |
| 3 | `Send this exact bulletin to Telegram: AI research digest ready. Ask me to confirm before sending.` | `send` (`needs_confirmation`) | `starter_v0/transcripts/v5_ollama_20261110T185614797492.transcript.json` (v5) | Model gọi `send` quá sớm; guard của tool chặn, không có tin nhắn nào được gửi. UI còn yêu cầu bấm xác nhận trực tiếp trước khi gửi. |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới `doi_lookup` | `starter_v0/tools/doi_lookup/tool.py`, `TOOL.md`, `tools/__init__.py`, `artifacts/tools.yaml` | Nhận DOI hoặc URL doi.org và trả metadata Crossref; có case `G01_lookup_exact_doi` trong `data/eval_group.json` | DOI sai hoặc lỗi HTTP trả error dict, không raise |
| 3 unit test `doi_lookup` | `starter_v0/tests/test_tools_todo.py`; `python -m pytest -q`: 71 passed, 14 skipped, 0 failed | Kiểm tra metadata + URL request, input sai kiểu không gọi HTTP, HTTP 429 trả error dict | HTTP được mock; chưa kiểm chứng API thật |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`; `streamlit run app.py`; https://fuel-review-excess-control.trycloudflare.com | Streamlit mở local và qua Quick Tunnel, health check HTTP 200; lưu transcript cho từng phiên | Link tạm thời; cần giữ máy demo và tunnel hoạt động. Nút xác nhận trong UI chặn gửi Telegram tự động. |

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

- Model `qwen3:1.7b` vẫn có thể bỏ qua ranh giới trong prompt: ở live chat, lượt thiếu URL không gọi `clarify`; lượt gửi Telegram gọi `send` trước xác nhận. Tool `send` trả `needs_confirmation`, và UI còn yêu cầu bấm nút xác nhận trực tiếp trước khi gửi. Bằng chứng: bảng B4 và các transcript được dẫn tại đó.
- Eval nhóm ban đầu chỉ kiểm tra tên tool `format`, khiến case G04 pass dù model không truyền `items`. Nhóm thêm kiểm tra tham số và phát hiện lỗi; run cuối trong bảng B3 có 8/10 case pass.
- Bộ chấm ban đầu gây `TypeError` khi so sánh danh sách object trong `items`. Nhóm sửa `run_eval.py` và thêm `tests/test_eval_scoring.py`; suite hiện 71 pass, 14 TODO skip, 0 fail.
- Trên PowerShell, CLI ban đầu lỗi encoding khi in tiếng Việt/emoji. Nhóm cấu hình stdout UTF-8 trong `chat.py` và chạy lại transcript live hợp lệ.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
