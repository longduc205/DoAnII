# UML Diagrams

> **Phase:** Phase 2 - System Architecture Design
> **Day:** Day 14
> **Generated:** 2026-04-30

---

## 1. Use Case Diagram

```mermaid
use case
  "User" as U
  "System" as S
  "AI Module" as AI

  U --> (Start Scan)
  U --> (View Results)
  U --> (View History)
  U --> (Export Report)
  U --> (Delete Scan)

  (Start Scan) ..> (Validate URL) : include
  (Start Scan) ..> (Crawl Pages) : include
  (Start Scan) ..> (Detect Vulnerabilities) : include
  (Start Scan) ..> (AI Classification) : include
  (Start Scan) ..> (Save Results) : include

  (Detect Vulnerabilities) ..> (Test SQLi) : include
  (Detect Vulnerabilities) ..> (Test XSS) : include

  (View Results) ..> (AI Classification) : include
```

| Actor | Description |
|-------|-------------|
| User | Người dùng tương tác với hệ thống qua giao diện web |
| System | AI Web Vulnerability Scanner (Flask app) |
| AI Module | Mô-đun phân loại phản hồi HTTP bằng ML |

| Use Case | Description |
|----------|-------------|
| Start Scan | Nhập URL, bắt đầu quét toàn bộ pipeline |
| Validate URL | Kiểm tra URL hợp lệ và có thể truy cập |
| Crawl Pages | Thu thập pages và forms từ target |
| Detect Vulnerabilities | Thử nghiệm SQLi và XSS payloads |
| AI Classification | Trích xuất features, phân loại phản hồi |
| Save Results | Lưu kết quả vào database |
| View Results | Xem chi tiết kết quả sau khi scan xong |
| View History | Xem lịch sử các scan đã thực hiện |
| Export Report | Xuất báo cáo ra file |
| Delete Scan | Xóa một scan session khỏi lịch sử |

---

## 2. Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Web UI
    participant Route as /scan
    participant Scanner as Scanner Engine
    participant Crawler
    participant Detector
    participant AI as AI Module
    participant DB as Database

    User->>UI: Enter target URL
    UI->>Route: POST /scan {url}
    Route->>Scanner: start_scan(url)

    Scanner->>Scanner: validate_url(url)
    Scanner->>DB: create_scan_session()
    Scanner->>Crawler: crawl(url)

    loop BFS crawl
        Crawler->>Crawler: fetch_page(url)
        Crawler->>Crawler: extract_forms(html)
        Crawler->>Crawler: discover_links()
    end
    Crawler-->>Scanner: pages[], forms[]
    Scanner->>DB: save_pages(pages)

    loop For each form
        Scanner->>Detector: test_sqli(form)
        loop For each SQLi payload
            Detector->>Detector: send_request(form, payload)
            Detector->>Detector: compare_baseline_vs_response()
        end
        Detector-->>Scanner: sqli_results[]

        Scanner->>Detector: test_xss(form)
        loop For each XSS payload
            Detector->>Detector: send_request(form, payload)
            Detector->>Detector: check_reflection()
        end
        Detector-->>Scanner: xss_results[]

        alt Model exists
            Scanner->>AI: extract_features(response)
            AI-->>Scanner: features[]
            Scanner->>AI: predict(features)
            AI-->>Scanner: classification, confidence
        else No model
            Scanner-->>Scanner: skip AI
        end
    end

    Scanner->>DB: save_vulnerabilities()
    Scanner-->>Route: scan_id
    Route-->>UI: redirect /results/<scan_id>
    UI-->>User: Display results page
```

**Ghi chu:** Nhanh `alt/else` cho AI model fallback logic - neu chua co model trained, he thong van chay binh thuong chi khong co AI classification.

---

## 3. Activity Diagram (Scan Process)

```mermaid
flowchart TD
    A([Start]) --> B[/Input Target URL/]
    B --> C{URL valid?}
    C -->|No| D[/Show Error Message/]
    C -->|Yes| E[Create Scan Session]
    E --> F[Crawl Target Website]
    F --> G{More pages\nfound?}
    G -->|Yes| H[Extract Forms]
    H --> G
    G -->|No| I{For each\nform?}
    I -->|Yes| J[/Select Form/]
    J --> K{More payloads\nto test?}
    K -->|Yes| L[Send Test Request\nwith Payload]
    L --> M{Test SQLi\ndetected?}
    M -->|Yes| N[Save SQLi\nVulnerability]
    M -->|No| O{Test XSS\ndetected?}
    O -->|Yes| P[Save XSS\nVulnerability]
    O -->|No| Q{AI model\navailable?}
    K -->|No| Q
    N --> Q
    P --> Q
    Q -->|Yes| R[Extract Features\nfrom Response]
    R --> S[AI Classify:\nnormal/suspicious]
    S --> T[Save AI Result]
    Q -->|No| I
    T --> I
    I -->|All forms\ndone| U[Save Scan\nResults to DB]
    U --> V[/Display Results\nPage/]
    V --> Z([End])
    D --> Z

    style A fill:#e3f2fd,stroke:#1565c0
    style Z fill:#e8f5e9,stroke:#2e7d32
    style D fill:#ffebee,stroke:#c62828
    style N fill:#fff3e0,stroke:#e65100
    style P fill:#fff3e0,stroke:#e65100
    style S fill:#f3e5f5,stroke:#7b1fa2
    style V fill:#e8f5e9,stroke:#2e7d32
```

**Tom tat flow:**
1. Nhap URL -> kiem tra hop le
2. Tao session -> crawl pages -> extract forms
3. Moi form: thu SQLi -> thu XSS -> AI classify (neu co model)
4. Luu ket qua -> hien thi trang results
