# 🛡️ AI Web Vulnerability Scanner - Tổng quan & Kiến thức cốt lõi

Tài liệu này tổng hợp toàn bộ các nội dung, kiến thức lý thuyết và thực hành cần thiết để hiểu rõ về dự án **AI Web Vulnerability Scanner** (Đồ án II).

## 1. 📋 Tổng quan dự án (Project Overview)

Dự án là một trình quét lỗ hổng web tích hợp AI (AI-integrated web vulnerability scanner). Hệ thống kết hợp giữa phương pháp kiểm tra dựa trên luật (rule-based testing) truyền thống để phát hiện lỗ hổng và sử dụng **Generative AI (LLMs)** để phân tích, giải thích và đưa ra hướng dẫn khắc phục cụ thể cho từng lỗ hổng.

**Quy trình hoạt động chính:**
1. **Input**: Nhận URL mục tiêu từ người dùng.
2. **Crawl**: Thu thập dữ liệu trang web, tìm kiếm các trang (pages) và các biểu mẫu (forms) có thể nhập liệu.
3. **Scan (Rule-based)**: Tự động inject các payload độc hại (SQLi, XSS) vào các trường nhập liệu và gửi request để tìm lỗ hổng.
4. **AI Remediation**: Gửi bằng chứng (evidence) của lỗ hổng cho LLM (Blackbox AI / Gemini) để giải thích lý do phát hiện và tạo ra hướng dẫn sửa lỗi (remediation steps) cùng với code ví dụ.
5. **Interactive Q&A**: Cho phép người dùng chat trực tiếp với AI để hỏi đáp chi tiết về lỗ hổng vừa tìm thấy.

## 2. 🏗️ Kiến trúc hệ thống (System Architecture)

Hệ thống được chia thành nhiều module rõ ràng, tuân theo mô hình MVC (Model-View-Controller) của Flask:

- **Web Interface (Frontend)**: Giao diện người dùng được xây dựng bằng HTML, CSS, JS và Jinja2. Quản lý việc cấu hình scan, xem lịch sử và chat với AI.
- **Crawler Service**: Module chịu trách nhiệm duyệt qua cấu trúc website (sử dụng BFS) để trích xuất đường dẫn và biểu mẫu.
- **Scanner & Detector**: Engine cốt lõi thực thi các bài kiểm tra bảo mật bằng cách so sánh phản hồi bất thường so với phản hồi gốc.
- **AI Advisor Service**: Phân hệ Trí tuệ Nhân tạo kết nối với API của các LLM (như Blackbox AI DeepSeek-V3) bằng Prompt Engineering để tạo ra các lời khuyên bảo mật.
- **Database Layer**: Sử dụng SQLite (qua SQLAlchemy ORM) để lưu trữ phiên scan, trang đã tìm thấy, lỗ hổng phát hiện và các giải thích của AI.

## 3. 🧠 Các kiến thức nền tảng cần nắm (Core Knowledge)

### A. Kiến thức Web & HTTP
- **Mô hình Client-Server**: Cách trình duyệt giao tiếp với máy chủ web.
- **Giao thức HTTP/HTTPS**: Phương thức (GET, POST), Headers, Status Codes và Body.
- **DOM & HTML Parsing**: Dùng thư viện (như BeautifulSoup) để trích xuất `<form>`, `<input>`, `<a>`.

### B. Kiến thức An toàn thông tin (Web Security)
- **SQL Injection (SQLi)**: Khai thác lỗ hổng khi dữ liệu đầu vào không được làm sạch, làm thay đổi câu lệnh SQL.
- **Cross-Site Scripting (XSS)**: Chèn mã script độc hại vào trang web để chạy trên trình duyệt nạn nhân.
- **Remediation**: Cách sửa lỗi thực tế (Parameterized Queries cho SQLi, Output Encoding cho XSS).

### C. Web Crawling & Automation
- **Thuật toán BFS/DFS**: Duyệt qua các liên kết nội bộ của trang web.
- **Tự động hóa HTTP Requests**: Sử dụng `requests` để tự động hóa việc điền form và bắt phản hồi.

### D. Trí tuệ Nhân tạo / Generative AI
- **Large Language Models (LLMs)**: Cách các mô hình ngôn ngữ lớn như GPT, Gemini, DeepSeek phân tích văn bản và sinh mã.
- **Prompt Engineering**: Cách thiết kế câu lệnh (prompt) chuyên biệt để ép AI đóng vai trò làm Chuyên gia Bảo mật (Security Expert), trả về định dạng JSON chuẩn.
- **API Integration**: Cách gọi API của bên thứ 3 (REST API), xử lý JSON payload, và Authentication (Bearer Token).

## 4. 🛠️ Công nghệ sử dụng (Tech Stack)

- **Ngôn ngữ**: Python 3.11+
- **Web Framework**: Flask, Jinja2 Templates
- **Cơ sở dữ liệu**: SQLite (qua ORM SQLAlchemy)
- **Thư viện Web Crawling**: `requests`, `BeautifulSoup4`
- **AI Integration**: Giao tiếp qua HTTP Requests tới OpenAI-compatible endpoints (Blackbox AI).
- **Môi trường & Triển khai**: Docker & Docker Compose.

## 5. 📂 Cấu trúc thư mục dự án

- `/app`: Chứa mã nguồn Flask application (routes, models, templates, utils).
- `/app/services`: Các thành phần logic chính: `crawler.py`, `scanner.py`, `detector.py`, `ai_advisor.py`.
- `/data`: Chứa payloads cho SQLi, XSS.
- `/tests`: Các kịch bản kiểm thử cho từng tính năng.
- `/templates`: Chứa giao diện Dashboard, Report và AI Chat.

## 6. 🚀 Các lệnh vận hành dự án

- **Khởi động môi trường ảo**: `source venv/bin/activate`
- **Chạy với Docker**: `docker compose up --build`
- **Chạy ứng dụng (Dev)**: `python run.py`
- **Khởi tạo Database**: `python -m app.utils.db_init`
- **Chạy Unit Test**: `pytest tests/ -v`

---
> **Lưu ý đạo đức**: Công cụ này được thiết kế và xây dựng **chỉ vì mục đích học thuật và giáo dục**. Cần xác minh lại các tư vấn của AI trước khi áp dụng vào mã nguồn thực tế.
