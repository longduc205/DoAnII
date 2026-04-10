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
- [ ] **🎯 Học**: Tìm hiểu kiến trúc web application (client-server model, request-response)
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
  - [PortSwigger: SQL Injection](https://portswigger.net/web-security/sql-injection)

### Ngày 5-6: Cross-Site Scripting (XSS) Theory  
- [ ] **🎯 Học**: Hiểu sâu về XSS
  - XSS là gì? Các loại: Reflected, Stored, DOM-based
  - Cách hoạt động: untrusted input → render trên browser
  - Impact: cookie theft, session hijacking, defacement
  - Cách phòng chống: Output encoding, Content Security Policy
- [ ] **📝 Viết**: Draft phần "Cross-Site Scripting" cho Chapter 1 & 2
- [ ] **📝 Thực hành**: Test thử XSS trên DVWA
- [ ] **📚 Đọc**:
  - [OWASP: XSS](https://owasp.org/www-community/attacks/xss/)
  - [PortSwigger: XSS](https://portswigger.net/web-security/cross-site-scripting)

### Ngày 7-8: Web Crawling & Vulnerability Scanner Theory
- [ ] **🎯 Học**: Tìm hiểu về web crawling và vulnerability scanning
  - Web crawler hoạt động như thế nào? BFS vs DFS
  - Vulnerability scanner workflow: crawl → test → analyze → report
  - Các scanner phổ biến: OWASP ZAP, Nikto, Burp Suite
  - Hạn chế của scanner truyền thống (rule-based, false positives)
- [ ] **📝 Viết**: Draft phần "Vulnerability Scanning" cho Chapter 1
- [ ] **📚 Đọc**:
  - [OWASP ZAP Documentation](https://www.zaproxy.org/docs/)
  - Research papers về automated vulnerability scanning

### Ngày 9-10: AI/ML in Cybersecurity
- [ ] **🎯 Học**: Tìm hiểu AI/ML trong cybersecurity
  - Supervised Learning: classification concepts
  - Logistic Regression & Random Forest: cách hoạt động
  - Feature engineering cho security data
  - Evaluation metrics: Accuracy, Precision, Recall, F1-score
  - Tại sao AI hỗ trợ được vulnerability scanning?
- [ ] **📝 Viết**: Draft phần "AI in Cybersecurity" cho Chapter 1 & 2
- [ ] **📚 Đọc**:
  - [Scikit-learn: Classification](https://scikit-learn.org/stable/supervised_learning.html)
  - Research papers: "Machine Learning for Web Vulnerability Detection"

### 📌 Phase 1 Deliverables
- [ ] Draft Introduction
- [ ] Draft Chapter 1 (Overview)
- [ ] Draft Chapter 2 (Theoretical Background) - phần lớn

---

## Phase 2: Requirement Analysis & System Design (Tuần 3)

> **Mục đích**: Phân tích yêu cầu, thiết kế kiến trúc hệ thống, vẽ UML

### Ngày 11-12: Requirement Analysis
- [ ] **🎯 Học**: System requirements analysis methodology
  - Functional vs Non-functional requirements
  - Use case analysis
  - Phân tích yêu cầu cho hệ thống scanner
- [ ] **📝 Viết**: Functional Requirements
  - FR1: Nhận URL target từ người dùng
  - FR2: Crawl website, phát hiện pages & forms
  - FR3: Test SQLi trên các form tìm được
  - FR4: Test XSS trên các form tìm được
  - FR5: AI classify response (normal/suspicious)
  - FR6: Tạo báo cáo kết quả scan
  - FR7: Lưu lịch sử scan
- [ ] **📝 Viết**: Non-functional Requirements
  - Usability, Modularity, Maintainability, Security

### Ngày 13: System Architecture Design
- [ ] **🎯 Thiết kế**: Kiến trúc tổng thể hệ thống
  - Vẽ System Architecture Diagram
  - Mô tả data flow: User Input → Crawler → Detector → AI → Report
  - Xác định các module và interaction giữa chúng
- [ ] **📝 Lưu**: `docs/diagrams/system_architecture.png`

### Ngày 14: UML Diagrams
- [ ] **🎯 Vẽ**: Use Case Diagram
  - Actor: User
  - Use cases: Start Scan, View Results, View History, Export Report
- [ ] **🎯 Vẽ**: Sequence Diagram
  - Flow: User → WebUI → Scanner → Crawler → Detector → AI → DB → Report
- [ ] **🎯 Vẽ**: Activity Diagram (optional)
- [ ] **📝 Lưu**: `docs/diagrams/`

### Ngày 15: Database Design
- [ ] **🎯 Thiết kế**: Database schema
  - Table: `scans` (scan sessions)
  - Table: `pages` (discovered pages)
  - Table: `vulnerabilities` (findings)
  - Table: `ai_results` (AI classifications)
  - Vẽ ER Diagram
- [ ] **📝 Review**: Kiểm tra lại models trong `app/models/`
- [ ] **📝 Lưu**: `docs/diagrams/er_diagram.png`

### 📌 Phase 2 Deliverables
- [ ] Draft Chapter 3 (System Analysis & Design)
- [ ] UML diagrams (Use Case, Sequence, Architecture)
- [ ] Database ER Diagram

---

## Phase 3: Core Scanner Development (Tuần 4-6)

> **Mục đích**: Xây dựng prototype hoạt động được: UI + Crawler + Detection

### Ngày 16-17: Development Environment Setup
- [ ] **🎯 Setup**: Môi trường phát triển
  - Tạo virtual environment: `python -m venv venv`
  - Install dependencies: `pip install -r requirements.txt`
  - Copy `.env.example` → `.env` và config
  - Test chạy Flask app: `python run.py`
  - Verify database initialization
- [ ] **📝 Kiểm tra**: App chạy được trên `http://localhost:5000`

### Ngày 18-20: Web Interface (Flask UI)
- [ ] **🎯 Học**: Flask basics (routes, templates, Jinja2, static files)
- [ ] **📝 Code**: `templates/base.html` - Base layout
  - Navigation bar (Home, Scan, History)
  - Footer, CSS styling
- [ ] **📝 Code**: `templates/index.html` - Home page
  - URL input form
  - Scan configuration options
  - "Start Scan" button
- [ ] **📝 Code**: `templates/scan.html` - Scan progress page
  - Scan status display
  - Live progress updates (optional)
- [ ] **📝 Code**: `templates/results.html` - Results page
  - Summary statistics
  - Vulnerability list with details
  - AI classification results
- [ ] **📝 Code**: `templates/history.html` - History page
  - List of past scans
  - Click to view details
- [ ] **📝 Code**: `app/static/css/style.css` - Styling
- [ ] **📝 Code**: `app/static/js/main.js` - Frontend logic
- [ ] **📝 Screenshot**: Chụp UI cho report → `docs/screenshots/`

### Ngày 21-24: Web Crawler Implementation
- [ ] **🎯 Học**: BeautifulSoup4 & Requests library
  - HTML parsing với BeautifulSoup
  - HTTP requests với Requests library
  - URL parsing với urllib.parse
- [ ] **📝 Code**: Hoàn thiện `app/services/crawler.py`
  - `crawl()` - BFS traversal từ base URL
  - `_fetch_page()` - Fetch & parse HTML
  - `_extract_links()` - Tìm tất cả internal links
  - `_extract_forms()` - Tìm forms và input fields
  - `_should_skip()` - Filter URLs không cần crawl
- [ ] **📝 Test**: Chạy crawler trên website test
  - Test với DVWA locally
  - Verify link extraction hoạt động
  - Verify form extraction hoạt động
- [ ] **📝 Code**: Viết tests trong `tests/test_crawler.py`

### Ngày 25-28: SQL Injection Detection
- [ ] **🎯 Học**: SQLi detection methodology
  - Baseline response comparison
  - Error-based detection (SQL error keywords)
  - Response length anomaly detection
  - Status code change detection
- [ ] **📝 Code**: Hoàn thiện `app/services/detector.py` - SQLi phần
  - `test_sqli()` - Inject payloads vào form parameters
  - `_get_baseline_response()` - Lấy response bình thường
  - `_compare_responses()` - So sánh baseline vs test
  - Error keyword matching
- [ ] **📝 Code**: Load payloads từ `data/payloads/sqli_payloads.txt`
- [ ] **📝 Test**: Test SQLi detection trên DVWA
- [ ] **📝 Code**: Viết tests trong `tests/test_detector.py`
- [ ] **📝 Screenshot**: Chụp kết quả detection

### Ngày 29-32: XSS Detection
- [ ] **🎯 Học**: XSS detection methodology
  - Reflected payload detection
  - Response content analysis
  - Script tag detection in response
- [ ] **📝 Code**: Hoàn thiện `app/services/detector.py` - XSS phần
  - `test_xss()` - Inject XSS payloads
  - Kiểm tra payload có bị reflect trong response không
  - Phát hiện script tags trong response
- [ ] **📝 Code**: Load payloads từ `data/payloads/xss_payloads.txt`
- [ ] **📝 Test**: Test XSS detection trên DVWA
- [ ] **📝 Screenshot**: Chụp kết quả detection

### Ngày 33-35: Scanner Engine Integration
- [ ] **📝 Code**: Hoàn thiện `app/services/scanner.py`
  - Kết nối Crawler → Detector pipeline
  - Lưu kết quả vào database
  - Error handling và logging
- [ ] **📝 Code**: Cập nhật routes để connect với Scanner Engine
  - `app/routes/scan.py` - Start scan, check status
  - `app/routes/results.py` - Query & display results
  - `app/routes/history.py` - Query scan history
- [ ] **📝 Test**: Full pipeline test: URL input → Crawl → Detect → Results
- [ ] **📝 Screenshot**: Chụp full workflow cho report

### 📌 Phase 3 Deliverables
- [ ] Working prototype: Web UI + Crawler + SQLi/XSS Detection
- [ ] Database storing scan results
- [ ] Unit tests cho crawler & detector
- [ ] Screenshots cho Chapter 4

---

## Phase 4: AI Module Integration (Tuần 7)

> **Mục đích**: Tích hợp ML model để classify responses

### Ngày 36-37: Data Collection & Feature Engineering
- [ ] **🎯 Học**: Feature engineering for security data
  - Features nào quan trọng để classify response?
  - Cách thu thập training data từ scan sessions
- [ ] **📝 Code**: Hoàn thiện `ai/feature_extractor.py`
  - Extract features từ HTTP responses
  - Features: response_length, status_code, keyword presence, reflection
- [ ] **📝 Tạo**: Training dataset
  - Chạy scanner trên DVWA (vulnerable pages → label "suspicious")
  - Chạy scanner trên normal pages (→ label "normal")
  - Lưu vào `data/raw/training_data.csv`

### Ngày 38-39: Model Training
- [ ] **🎯 Học**: Scikit-learn classification pipeline
  - Train/test split
  - Model fitting
  - Evaluation metrics interpretation
- [ ] **📝 Code**: Hoàn thiện `ai/preprocessor.py`
  - Normalize features
  - Handle missing values
- [ ] **📝 Code**: Hoàn thiện `ai/trainer.py`
  - Fix import error (`sklearn.ensemble`)
  - Train LogisticRegression
  - Train RandomForest (so sánh)
  - Evaluate: accuracy, precision, recall, F1-score
  - Save best model → `ai/models/classifier.pkl`
- [ ] **📝 Ghi lại**: Training results cho report

### Ngày 40-41: AI Integration into Pipeline
- [ ] **📝 Code**: Hoàn thiện `ai/predictor.py`
  - Load trained model
  - Predict trên new responses
- [ ] **📝 Code**: Hoàn thiện `app/services/ai_analyzer.py`
  - Kết nối Predictor vào scanning pipeline
  - Classify mỗi response sau khi detect
- [ ] **📝 Code**: Cập nhật `app/services/scanner.py`
  - Thêm AI analysis step vào pipeline
  - Lưu AI results vào database
- [ ] **📝 Code**: Cập nhật `templates/results.html`
  - Hiển thị AI classification bên cạnh rule-based results
  - Hiển thị confidence score

### Ngày 42: AI Module Testing
- [ ] **📝 Test**: End-to-end test với AI module
  - Verify model loads correctly
  - Verify classification results make sense
  - Test edge cases
- [ ] **📝 Code**: Hoàn thiện tests trong `tests/test_ai_analyzer.py`
- [ ] **📝 Screenshot**: Chụp AI results cho report

### 📌 Phase 4 Deliverables
- [ ] Trained ML model (`ai/models/classifier.pkl`)
- [ ] AI integrated into scanning pipeline
- [ ] Training evaluation metrics cho Chapter 5
- [ ] Screenshots cho Chapter 4

---

## Phase 5: Testing & Evaluation (Tuần 8)

> **Mục đích**: Testing hệ thống, thu thập kết quả, đánh giá

### Ngày 43-44: Functional Testing
- [ ] **📝 Test**: Test từng chức năng
  - ✅ URL input validation
  - ✅ Crawler discovers pages & forms correctly
  - ✅ SQLi detection finds known vulnerabilities
  - ✅ XSS detection finds known vulnerabilities
  - ✅ AI classification runs without errors
  - ✅ Results stored in database
  - ✅ Report generation works
  - ✅ History page shows past scans
- [ ] **📝 Ghi lại**: Kết quả testing vào bảng

### Ngày 45-46: Performance Evaluation
- [ ] **📝 Test**: Test trên multiple targets
  - DVWA (Damn Vulnerable Web Application)
  - WebGoat (OWASP)
  - Custom test pages (nếu có)
- [ ] **📝 Đánh giá**: Scanner performance
  - True Positives: Phát hiện đúng vulnerability
  - False Positives: Báo sai
  - True Negatives: Bỏ qua đúng
  - False Negatives: Bỏ sót vulnerability
- [ ] **📝 Đánh giá**: AI model performance
  - Accuracy, Precision, Recall, F1-score
  - Confusion matrix
  - So sánh với rule-based only

### Ngày 47-48: Strengths & Limitations Analysis
- [ ] **📝 Viết**: Điểm mạnh
  - Tích hợp AI + rule-based scanning
  - Modular architecture, dễ mở rộng
  - Giá trị giáo dục
  - Tự động hóa quy trình scan
- [ ] **📝 Viết**: Hạn chế
  - Coverage giới hạn (chỉ SQLi, XSS)
  - Training data ít
  - Crawler đơn giản (không handle JavaScript)
  - Không support authenticated scanning
- [ ] **📝 Viết**: Draft Chapter 5 (Testing & Evaluation)

### 📌 Phase 5 Deliverables
- [ ] Complete testing results
- [ ] AI evaluation metrics (accuracy, precision, recall, F1)
- [ ] Draft Chapter 5
- [ ] Screenshots các test scenarios

---

## Phase 6: Report Writing & Revision (Tuần 9)

> **Mục đích**: Hoàn thiện báo cáo, review, chuẩn bị bảo vệ

### Ngày 49-51: Final Report Assembly
- [ ] **📝 Viết**: Hoàn thiện Introduction
  - Background, problem statement, objectives, scope
- [ ] **📝 Review**: Chapter 1 - Overview
  - Web security context, vulnerability types, scanner role, AI in security
- [ ] **📝 Review**: Chapter 2 - Theoretical Background
  - Web architecture, HTTP, crawling, SQLi theory, XSS theory, AI/ML theory
- [ ] **📝 Review**: Chapter 3 - System Analysis & Design
  - Requirements, architecture, UML diagrams, database design
- [ ] **📝 Review**: Chapter 4 - Implementation
  - Technologies, UI, crawler, detector, AI module, report generation
- [ ] **📝 Review**: Chapter 5 - Testing & Evaluation
  - Test environment, scenarios, results, AI metrics, strengths/limitations

### Ngày 52-53: Conclusion & Future Work
- [ ] **📝 Viết**: Conclusion
  - Tóm tắt contributions
  - Academic value
  - Practical usefulness
- [ ] **📝 Viết**: Future Work
  - Thêm vulnerability types (CSRF, IDOR, etc.)
  - Improve crawler (JavaScript rendering)
  - Larger training dataset
  - Explainable AI decisions
  - Extend thành platform hoàn chỉnh cho Đồ Án 3 / Khóa luận

### Ngày 54-55: Formatting & Polish
- [ ] **📝 Check**: Grammar & spelling (English)
- [ ] **📝 Check**: Consistent terminology
- [ ] **📝 Check**: Figure numbering & captions
- [ ] **📝 Check**: Table formatting
- [ ] **📝 Check**: References (APA/IEEE format)
- [ ] **📝 Check**: Chapter transitions
- [ ] **📝 Check**: Academic tone throughout

### Ngày 56: Presentation Preparation
- [ ] **📝 Tạo**: Slide thuyết trình
  - Slide 1: Title
  - Slide 2-3: Problem & Objectives
  - Slide 4-5: Architecture & Design
  - Slide 6-8: Implementation highlights
  - Slide 9-10: Results & Evaluation
  - Slide 11: Demo
  - Slide 12: Conclusion & Future Work
- [ ] **📝 Chuẩn bị**: Demo scenario

### 📌 Phase 6 Deliverables
- [ ] Complete academic report (English)
- [ ] Presentation slides
- [ ] Demo ready

---

## 📊 Weekly Progress Tracker

| Tuần | Phase | Trọng tâm | Status |
|------|-------|-----------|--------|
| 1-2  | Phase 1 | Literature Review & Theory | `[ ]` |
| 3    | Phase 2 | Requirements & Design | `[ ]` |
| 4-5  | Phase 3a | Web UI + Crawler | `[ ]` |
| 6    | Phase 3b | SQLi/XSS Detection | `[ ]` |
| 7    | Phase 4 | AI Module | `[ ]` |
| 8    | Phase 5 | Testing & Evaluation | `[ ]` |
| 9    | Phase 6 | Report & Presentation | `[ ]` |

---

## 🛠️ Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
python run.py

# Run tests
pytest tests/ -v

# Initialize database
python -m app.utils.db_init

# Train AI model
python -m ai.trainer
```

---

## 📚 Key References

1. **OWASP Top 10**: https://owasp.org/www-project-top-ten/
2. **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
3. **PortSwigger Web Security Academy**: https://portswigger.net/web-security
4. **Flask Documentation**: https://flask.palletsprojects.com/
5. **Scikit-learn Documentation**: https://scikit-learn.org/stable/
6. **BeautifulSoup Documentation**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
7. **DVWA (Damn Vulnerable Web Application)**: https://github.com/digininja/DVWA

---

> 💡 **Tip**: Mỗi ngày dành ít nhất 30 phút đọc tài liệu + 1-2 giờ code/viết. Consistency quan trọng hơn intensity!
