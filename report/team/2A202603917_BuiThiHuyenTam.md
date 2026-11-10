# Báo cáo cá nhân — Bùi Thị Huyền Tâm

## 1. Thông tin thành viên

- Họ tên: Bùi Thị Huyền Tâm
- MSSV: 2A202603917
- Email: Chưa được cung cấp.

## 2. Phần việc phụ trách

- Phụ trách xây dựng giao diện web Streamlit để người dùng chọn provider/model, chat với Research Agent và xem hoạt động của các tool.
- Hỗ trợ thiết lập môi trường chạy và kiểm tra kết nối Gemini.

## 3. Đóng góp cụ thể

- Tạo `starter_v0/app.py` bằng Streamlit: giao diện chat, chọn provider và model, hiển thị chi tiết tool calls, báo lỗi provider và lưu transcript JSON.
- Thêm Streamlit vào `starter_v0/requirements.txt`.
- Tắt tool `send` trong UI để không gửi tin ra Telegram khi chưa có bước xác nhận riêng.
- Tạo và kích hoạt môi trường ảo Python `.venv`; cấu hình Gemini API key trong `starter_v0/.env` (key được giữ cục bộ, không đưa vào repository).
- Điều tra lỗi Gemini: `gemini-2.5-flash` trả 404 với tài khoản mới; model mặc định trong `providers/gemini_provider.py` được đổi sang `gemini-3.8-flash`. Một lần gọi sau đó trả 503 do model quá tải tạm thời.
- Chạy baseline v0 bằng `gemini-3.5-flash-lite`: 20/20 case được đo, 0 provider error, 13/20 case đạt (65% case accuracy), 80% tool routing, 65% argument accuracy và 66.67% multi-turn accuracy. Các lỗi chính: 3 `wrong_tool`, 2 `missing_info`, 1 `wrong_boundary`, 1 `wrong_arg_value`.

## 4. Bằng chứng

- File/commit/PR:
  - `starter_v0/app.py` — giao diện Streamlit.
  - `starter_v0/requirements.txt` — dependency Streamlit.
  - `starter_v0/providers/gemini_provider.py` — model Gemini mặc định.
  - `starter_v0/transcripts/v0_gemini_20261110T182406804229.transcript.json` — transcript lần chạy gặp lỗi 404 với model 2.5.
  - `starter_v0/runs/v0_B_base_gemini_20261110T193241444893.json` — baseline v0 với Gemini 3.5 Flash-Lite; 20 case đo, 13 case đạt, 0 provider error.
  - Chưa có commit/PR được ghi nhận.
- Cách chạy UI: từ thư mục `starter_v0/`, chạy `python -m pip install -r requirements.txt`, sau đó `streamlit run app.py`. UI cần provider key hợp lệ trong `.env`.
- AI/công cụ đã dùng và cách tự kiểm tra: dùng trợ lý AI để đọc README, phân tích traceback và hỗ trợ triển khai giao diện; đối chiếu kết quả eval với run JSON nêu trên. UI chưa có transcript chat riêng nên chưa xác nhận chạy end-to-end; cần khởi chạy UI và thực hiện chat thật để bổ sung bằng chứng.

## 5. Tự đánh giá

Đã bổ sung giao diện chọn provider/model, chat, xem tool activity và lưu transcript; tool gửi Telegram bị tắt trong UI để tránh hành động ngoài ý muốn. Baseline đã chạy thành công nhưng accuracy mới đạt 65%, cần phân tích case lỗi và tiếp tục tối ưu prompt/tool. Phần UI chưa được kiểm tra end-to-end. Email chưa có trong thông tin dự án.
