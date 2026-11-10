# Báo cáo cá nhân — Mai Danh Hiếu (2A202603948)

## 1. Thông tin thành viên

- Họ tên: Mai Danh Hiếu
- MSSV: 2A202603948
- Email: 26ai.hieumd@vinuni.edu.vn

## 2. Phần việc phụ trách

- Thiết lập provider Ollama và đo baseline; tối ưu prompt/tool declaration qua các phiên bản v1–v5.
- Xây dựng tool `doi_lookup`, eval nhóm, UI và ghi transcript live.

## 3. Đóng góp cụ thể

- Ghi run v0–v5 và `artifacts/version_log.csv`; baseline 5/20, v5 base 7/20. Các run này đo đủ 20 case và không có lỗi provider.
- Thêm `doi_lookup` tra metadata Crossref, đăng ký trong registry và tool declaration; viết 3 unit test cho đường thành công, input sai và HTTP 429.
- Viết 10 case eval nhóm (5 single turn, 5 multi turn); run cuối v5 đạt 8/10, không có lỗi provider.
- Thêm Streamlit UI và lưu transcript. Live chat bộc lộ lỗi model gọi `send` trước xác nhận; tool trả `needs_confirmation` để chặn gửi.
- Sửa lỗi so sánh danh sách object trong bộ chấm và thêm `tests/test_eval_scoring.py`.

## 4. Bằng chứng

- Commit kỹ thuật: `0fa6e99` (baseline), `3af0bde`–`cc189bb` (v1–v5), `79023a9` (tool và eval), `aebc519` (UI và báo cáo). Xem lịch sử Git để kiểm tra thay đổi cụ thể.
- File: `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/`, `starter_v0/tools/doi_lookup/`, `starter_v0/data/eval_group.json`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/test_eval_scoring.py`, `starter_v0/app.py`, `starter_v0/transcripts/`.
- Tự kiểm tra bằng `python -m pytest -q` từ `starter_v0/`: 71 passed, 14 skipped, 0 failed; đối chiếu `summary` của run JSON và bảng B1–B4 trong báo cáo nhóm. Các test còn skipped thuộc phần TODO của tool có sẵn.

## 5. Tự đánh giá

Đã tạo được vòng đo có bằng chứng và tool mới có test. Hạn chế chính là độ chính xác base v5 mới đạt 7/20; model vẫn sai ở xử lý thông tin thiếu và ranh giới xác nhận gửi. Cần tiếp tục kiểm tra bằng hội thoại nhiều lượt và cải thiện routing trước khi dùng thật.
