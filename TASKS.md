# 📋 AI Web Vulnerability Scanner - Task Breakdown

> Chia theo từng phase và ngày làm việc. Mỗi task có mục tiêu học tập và implementation cụ thể.
> Thời gian ước tính: **9 tuần** (~63 ngày làm việc)

---

## 🔖 Cách sử dụng file này

- `[ ]` = Chưa làm
- `[/]` = Đang làm
- `[x]` = Đã hoàn thành
- Mỗi task có **🎯 Mục tiêu** (học gì), **📝 Việc cần làm** (code/viết gì), và **📚 Tài liệu tham khảo**
- Đánh dấu `[x]` khi hoàn thành task

---

## Phase 1: Literature Review & Topic Refinement (Tuần 1-2)

> **Mục đích**: Xây dựng nền tảng lý thuyết, hiểu rõ domain trước khi code

### Ngày 1-2: Web Application Security Fundamentals
- [x] **🎯 Học**: Tìm hiểu kiến trúc web application (client-server model, request-response)
  - HTTP/HTTPS protocol: methods (GET, POST), headers, status codes, body
  - Cách browser giao tiếp với server
  - Vai trò của backend, database trong web app
- [ ] **📝 Viết**: Draft phần "Web Application Architecture" cho Chapter 2
- [ ] **📚 Đọc**:
  - [MDN: HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
  - [OWASP: Web Application Security](https://owasp.org/www-project-web-security-testing-guide/)

### Ngày 3-4: SQL Injection Theory
- [ ] **🎯 Học**: Hiểu sâu về SQL Injection
  - SQL Injection là gì? Vì sao xảy ra?
  - Các loại SQLi: In-band, Blind, Out-of-band
  - Cách hoạt động: input không được sanitize → thay đổi query
  - Cách phòng chống: Parameterized queries, input validation
- [ ] **📝 Viết**: Draft phần "SQL Injection" cho Chapter 1 & 2
- [ ] **📝 Thực hành**: Test thử SQLi trên DVWA hoặc SQLi-labs
- [ ] **📚 Đọc**:
  - [OWASP: SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)

### Ngày 5-6: Cross-Site Scripting (XSS) Theory  
- [ ] **🎯 Học**: Hiểu sâu về XSS
  - XSS là gì? Các loại: Reflected, Stored, DOM-based
  - Cách hoạt động: untrusted input → render trên browser
  - Impact: cookie theft, session hijacking, defacement
  - Cách phòng chống: Output encoding, Content Security Policy
- [ ] **📝 Viết**: Draft phần "Cross-Site Scripting" cho Chapter 1 & 2
- [ ] **📝 Thực hành**: Test thử XSS trên DVWA

### Ngày 7-8: Web Crawling & Vulnerability Scanner Theory
- [ ] **🎯 Học**: Tìm hiểu về web crawling và vulnerability scanning
  - Web crawler hoạt động như thế nào? BFS vs DFS
  - Vulnerability scanner workflow: crawl → test → analyze → report
  - Các scanner phổ biến: OWASP ZAP, Nikto, Burp Suite
- [ ] **📝 Viết**: Draft phần "Vulnerability Scanning" cho Chapter 1

### Ngày 9-10: Generative AI in Cybersecurity
- [ ] **🎯 Học**: Tìm hiểu Generative AI và LLM trong an toàn thông tin
  - Prompt Engineering cơ bản
  - Sử dụng AI để phân tích và giải thích lỗ hổng
  - Cách tương tác với API của LLM (OpenAI, Gemini, Blackbox)
- [ ] **📝 Viết**: Draft phần "Generative AI in Cybersecurity" cho Chapter 1 & 2

### 📌 Phase 1 Deliverables
- [ ] Draft Introduction
- [ ] Draft Chapter 1 (Overview)
- [ ] Draft Chapter 2 (Theoretical Background) - phần lớn

---

## Phase 2: Requirement Analysis & System Design (Tuần 3)

> **Mục đích**: Phân tích yêu cầu, thiết kế kiến trúc hệ thống, vẽ UML

### Ngày 11-12: Requirement Analysis
- [x] **🎯 Học**: System requirements analysis methodology
- [x] **📝 Viết**: Functional Requirements
  - FR1: Nhận URL target từ người dùng
  - FR2: Crawl website, phát hiện pages & forms
  - FR3: Test SQLi, XSS trên các form tìm được
  - FR4: Tích hợp AI để tư vấn cách khắc phục (Remediation)
  - FR5: Cung cấp tính năng Chat Q&A với AI
  - FR6: Lưu lịch sử và báo cáo kết quả scan
- [x] **📝 Lưu**: `docs/requirements.md`

### Ngày 13: System Architecture Design
- [x] **🎯 Thiết kế**: Kiến trúc tổng thể hệ thống
  - Mô tả data flow: User Input → Crawler → Detector → AI Advisor → Report
- [x] **📝 Lưu**: `docs/diagrams/architecture.md`

### Ngày 14: UML Diagrams
- [x] **🎯 Vẽ**: Use Case Diagram & Sequence Diagram
- [x] **📝 Lưu**: `docs/diagrams/uml.md`

### Ngày 15: Database Design
- [x] **🎯 Thiết kế**: Database schema
  - Tables: `scans`, `pages`, `vulnerabilities`, `ai_results`
- [x] **📝 Lưu**: `docs/diagrams/er_diagram.md`

---

## Phase 3: Core Scanner Development (Tuần 4-6)

> **Mục đích**: Xây dựng prototype hoạt động được: UI + Crawler + Detection

### Ngày 16-17: Development Environment Setup
- [x] **🎯 Setup**: Môi trường phát triển Flask, Docker.

### Ngày 18-20: Web Interface (Flask UI)
- [x] **📝 Code**: Xây dựng giao diện cơ bản (Base layout, Dashboard, Scan Config, History).

### Ngày 21-24: Web Crawler Implementation
- [x] **📝 Code**: Hoàn thiện `app/services/crawler.py` (BFS traversal, extract links, forms).

### Ngày 25-28: SQL Injection Detection
- [x] **📝 Code**: Hoàn thiện `app/services/detector.py` (Error-based & Response length SQLi).

### Ngày 29-32: XSS Detection
- [x] **📝 Code**: Hoàn thiện `app/services/detector.py` (Reflected payload detection).

### Ngày 33-35: Scanner Engine Integration
- [x] **📝 Code**: Hoàn thiện `app/services/scanner.py` để chạy pipeline từ crawl đến detect và lưu DB.

---

## Phase 4: AI Remediation Advisor & LLM Integration (Tuần 7)

> **Mục đích**: Tích hợp LLM để cung cấp lời khuyên bảo mật và chat Q&A.

### Ngày 36-37: Prompt Engineering & API Setup
- [x] **🎯 Học**: Xây dựng prompt hiệu quả để AI đóng vai trò Security Expert.
- [x] **📝 Code**: Thiết lập kết nối API (sử dụng thư viện `requests` gọi đến Blackbox AI).
- [x] **📝 Code**: Xây dựng template JSON output mong muốn (Explanation, Remediation Steps, Code Example).

### Ngày 38-39: AI Advisor Service Implementation
- [x] **📝 Code**: Hoàn thiện `app/services/ai_advisor.py`.
  - Hàm `get_remediation()`: Gửi payload và evidence cho AI để phân tích tại sao lỗi xảy ra và cách sửa.
  - Xử lý các fallback template trong trường hợp API lỗi.
  - Parse JSON response trả về từ AI một cách an toàn.

### Ngày 40-41: Interactive AI Q&A Integration
- [x] **📝 Code**: Xây dựng API endpoint `/ai/ask` để chat.
- [x] **📝 Code**: Tạo giao diện Chat Panel trên trang `results.html`.
- [x] **📝 Code**: Cập nhật logic Javascript để gửi tin nhắn chat và render kết quả dạng Markdown/HTML.

### Ngày 42: End-to-End AI Testing
- [x] **📝 Test**: Kiểm tra luồng scan với AI kích hoạt.
  - Verify AI phân tích chính xác payload.
  - Verify chat panel hoạt động tốt khi đặt câu hỏi tùy chỉnh.

### 📌 Phase 4 Deliverables
- [x] AI Advisor module hoạt động ổn định.
- [x] Chat interface hoạt động mượt mà.
- [x] Tích hợp hoàn chỉnh AI vào Workflow.

---

## Phase 5: Testing & Evaluation (Tuần 8)

> **Mục đích**: Testing hệ thống, thu thập kết quả, đánh giá

### Ngày 43-44: Functional Testing
- [ ] **📝 Test**: Test từng chức năng
  - ✅ Crawler discovers pages & forms correctly
  - ✅ SQLi & XSS detection finds known vulnerabilities
  - ✅ AI provides relevant and accurate security advice
  - ✅ Report generation and History work
- [ ] **📝 Ghi lại**: Kết quả testing vào bảng

### Ngày 45-46: Performance Evaluation
- [ ] **📝 Test**: Test trên multiple targets (DVWA)
- [ ] **📝 Đánh giá**: Scanner performance (True Positives, False Positives).
- [ ] **📝 Đánh giá**: Chất lượng phản hồi của AI (Độ chính xác, tính hữu ích của code examples).

### Ngày 47-48: Strengths & Limitations Analysis
- [ ] **📝 Viết**: Điểm mạnh (Tích hợp AI Q&A, tự động hóa cao).
- [ ] **📝 Viết**: Hạn chế (Scanner chỉ là rule-based cơ bản, AI phụ thuộc API bên thứ 3).
- [ ] **📝 Viết**: Draft Chapter 5 (Testing & Evaluation)

---

## Phase 6: Report Writing & Revision (Tuần 9)

> **Mục đích**: Hoàn thiện báo cáo, review, chuẩn bị bảo vệ

### Ngày 49-56: Báo cáo & Thuyết trình
- [ ] **📝 Viết**: Hoàn thiện Introduction, Overview, Implementation, Conclusion.
- [ ] **📝 Check**: Formatting, References.
- [ ] **📝 Tạo**: Slide thuyết trình và chuẩn bị Demo scenario.

---

## 📊 Weekly Progress Tracker

| Tuần | Phase | Trọng tâm | Status |
|------|-------|-----------|--------|
| 1-2  | Phase 1 | Literature Review & Theory | `[x]` |
| 3    | Phase 2 | Requirements & Design | `[x]` |
| 4-5  | Phase 3a | Web UI + Crawler | `[x]` |
| 6    | Phase 3b | SQLi/XSS Detection | `[x]` |
| 7    | Phase 4 | AI Remediation & Chat | `[x]` |
| 8    | Phase 5 | Testing & Evaluation | `[ ]` |
| 9    | Phase 6 | Report & Presentation | `[ ]` |

---

## 🛠️ Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app locally
python run.py

# Run with Docker
docker compose up --build

# Initialize database
python -m app.utils.db_init

# Run unit tests
pytest tests/ -v
```

---

## 📚 Key References

1. **OWASP Top 10**: https://owasp.org/www-project-top-ten/
2. **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
3. **PortSwigger Web Security Academy**: https://portswigger.net/web-security
4. **Flask Documentation**: https://flask.palletsprojects.com/
5. **DVWA (Damn Vulnerable Web Application)**: https://github.com/digininja/DVWA
