# 🛡️ AI Web Vulnerability Scanner - Tổng quan & Kiến thức cốt lõi

Tài liệu này tổng hợp toàn bộ các nội dung, kiến thức lý thuyết và thực hành cần thiết để hiểu rõ về dự án **AI Web Vulnerability Scanner** (Đồ án II).

## 1. 📋 Tổng quan dự án (Project Overview)

Dự án là một trình quét lỗ hổng web tích hợp AI (AI-integrated web vulnerability scanner). Hệ thống kết hợp giữa phương pháp kiểm tra dựa trên luật (rule-based testing) truyền thống và phân loại phản hồi dựa trên học máy (machine-learning-assisted response classification) để tăng độ chính xác và giảm thiểu dương tính giả (false positives).

**Quy trình hoạt động chính:**
1. **Input**: Nhận URL mục tiêu từ người dùng.
2. **Crawl**: Thu thập dữ liệu trang web, tìm kiếm các trang (pages) và các biểu mẫu (forms) có thể nhập liệu.
3. **Scan (Rule-based)**: Tự động inject các payload độc hại (SQLi, XSS) vào các trường nhập liệu và gửi request.
4. **AI Analysis**: Sử dụng mô hình Machine Learning để phân tích HTTP Response và phân loại xem phản hồi đó là bình thường (normal) hay đáng ngờ (suspicious).
5. **Report**: Lưu kết quả vào cơ sở dữ liệu và hiển thị báo cáo cho người dùng.

## 2. 🏗️ Kiến trúc hệ thống (System Architecture)

Hệ thống được chia thành nhiều module rõ ràng, tuân theo mô hình MVC (Model-View-Controller) của Flask:

- **Web Interface (Frontend)**: Giao diện người dùng được xây dựng bằng HTML, CSS, JS và Jinja2 Templates. Quản lý việc cấu hình scan, xem lịch sử và kết quả.
- **Crawler Service**: Module chịu trách nhiệm duyệt qua cấu trúc website (sử dụng BFS - Breadth-First Search) để trích xuất các đường dẫn (links) và biểu mẫu (forms).
- **Scanner & Detector**: Engine cốt lõi thực thi các bài kiểm tra bảo mật (SQLi, XSS) bằng cách so sánh phản hồi bất thường so với phản hồi gốc (baseline response).
- **AI Module**: Phân hệ Trí tuệ Nhân tạo thực hiện trích xuất đặc trưng (feature extraction) từ HTTP response và dự đoán (predict) bằng mô hình đã được huấn luyện.
- **Database Layer**: Sử dụng SQLite (qua SQLAlchemy ORM) để lưu trữ phiên scan, trang đã tìm thấy, lỗ hổng phát hiện và kết quả phân loại của AI.

## 3. 🧠 Các kiến thức nền tảng cần nắm (Core Knowledge)

Để hiểu và phát triển dự án này, bạn cần nắm vững các mảng kiến thức sau:

### A. Kiến thức Web & HTTP (Web Architecture)
- **Mô hình Client-Server**: Cách trình duyệt (client) giao tiếp với máy chủ web (server).
- **Giao thức HTTP/HTTPS**: Hiểu rõ về các phương thức (GET, POST), Headers, Status Codes (200, 403, 404, 500), và Body.
- **DOM & HTML Parsing**: Cách cấu trúc một trang web và cách dùng thư viện (như BeautifulSoup) để trích xuất thẻ `<form>`, `<input>`, `<a>`.

### B. Kiến thức An toàn thông tin (Web Security)
- **SQL Injection (SQLi)**:
  - **Khái niệm**: Xảy ra khi dữ liệu đầu vào của người dùng không được kiểm tra/làm sạch, khiến câu lệnh SQL bị thay đổi.
  - **Dấu hiệu nhận biết**: Thay đổi mã trạng thái HTTP, xuất hiện từ khóa lỗi cơ sở dữ liệu, sự chênh lệch lớn về độ dài phản hồi (response length anomaly).
- **Cross-Site Scripting (XSS)**:
  - **Khái niệm**: Kẻ tấn công chèn các đoạn mã script độc hại (thường là JavaScript) vào trang web để chạy trên trình duyệt của nạn nhân.
  - **Dấu hiệu nhận biết**: Dữ liệu payload (chứa script tag) được phản hồi (reflect) trực tiếp về HTML của trang mà không qua mã hóa (encoding).

### C. Web Crawling & Automation
- **Thuật toán BFS/DFS**: Áp dụng duyệt cây/đồ thị để đi qua các liên kết nội bộ (internal links) của trang web.
- **Tự động hóa HTTP Requests**: Sử dụng thư viện (như `requests` trong Python) để quản lý cookies, headers, timeout và tự động hóa việc điền form.

### D. Trí tuệ Nhân tạo / Học máy (AI/ML in Cybersecurity)
- **Bài toán phân loại (Classification)**: Phân loại nhị phân (Binary Classification) để xác định HTTP response là Normal (Bình thường) hay Suspicious (Đáng ngờ).
- **Trích xuất đặc trưng (Feature Engineering)**: Biến đổi dữ liệu thô (HTTP response) thành các vector đặc trưng (ví dụ: độ dài phản hồi, số lượng ký tự đặc biệt, chứa mã lỗi không) để đưa vào mô hình AI.
- **Thuật toán & Đánh giá**: Sử dụng thuật toán như `Logistic Regression` hoặc `Random Forest` qua thư viện `scikit-learn`. Đánh giá mô hình dựa trên Accuracy, Precision, Recall và F1-Score.

## 4. 🛠️ Công nghệ sử dụng (Tech Stack)

- **Ngôn ngữ**: Python 3.9+
- **Web Framework**: Flask, Jinja2 Templates
- **Cơ sở dữ liệu**: SQLite (qua ORM SQLAlchemy)
- **Thư viện Web Crawling**: `requests`, `BeautifulSoup4`
- **Thư viện AI/ML**: `scikit-learn`, `pandas`, `numpy`
- **Môi trường & Triển khai**: Docker & Docker Compose (cho mục đích dễ dàng đóng gói và triển khai).

## 5. 📂 Cấu trúc thư mục dự án

- `/app`: Chứa mã nguồn Flask application (routes, models, templates, utils).
- `/app/services`: Các thành phần logic chính: `crawler.py`, `scanner.py`, `detector.py`, `ai_analyzer.py`.
- `/ai`: Phân hệ AI (trích xuất đặc trưng, huấn luyện mô hình, dự đoán).
- `/data`: Dữ liệu huấn luyện, dữ liệu thô và các danh sách tấn công (payloads cho SQLi, XSS).
- `/tests`: Các kịch bản kiểm thử cho từng tính năng.
- `/docs`: Tài liệu, sơ đồ UML.

## 6. 🚀 Các lệnh vận hành dự án

- **Khởi động môi trường ảo**: `source venv/bin/activate`
- **Chạy ứng dụng (Dev)**: `python run.py`
- **Chạy với Docker**: `docker compose up --build`
- **Khởi tạo Database**: `python -m app.utils.db_init`
- **Tạo dữ liệu huấn luyện AI**: `python scripts/generate_training_data.py`
- **Huấn luyện mô hình AI**: `python -m ai.trainer`
- **Chạy Unit Test**: `pytest tests/ -v`

---
> **Lưu ý đạo đức**: Công cụ này được thiết kế và xây dựng **chỉ vì mục đích học thuật và giáo dục**. Không sử dụng để quét vào các mục tiêu mà chưa được phép hoặc không có thẩm quyền.
