# UML Diagrams

> **Phase:** Phase 2 - System Architecture Design
> **Day:** Day 14
> **Generated:** 2026-04-30

---

## 1. Use Case Diagram

```mermaid
flowchart LR
    %% Actor
    User((User))

    %% System Boundary
    subgraph System [AI Web Vulnerability Scanner]
        direction TB
        StartScan([Start Scan])
        ViewResults([View Results])
        ViewHistory([View History])
        ExportReport([Export Report])
        DeleteScan([Delete Scan])

        ValidateURL([Validate URL])
        CrawlPages([Crawl Pages])
        DetectVuln([Detect Vulnerabilities])
        AIAdvisor([AI Remediation Advisor])
        SaveResults([Save Results])
        
        TestSQLi([Test SQLi])
        TestXSS([Test XSS])
    end

    %% Use Case Interactions
    User --> StartScan
    User --> ViewResults
    User --> ViewHistory
    User --> ExportReport
    User --> DeleteScan

    %% Includes
    StartScan -. "«include»" .-> ValidateURL
    StartScan -. "«include»" .-> CrawlPages
    StartScan -. "«include»" .-> DetectVuln
    StartScan -. "«include»" .-> AIAdvisor
    StartScan -. "«include»" .-> SaveResults

    DetectVuln -. "«include»" .-> TestSQLi
    DetectVuln -. "«include»" .-> TestXSS

    ViewResults -. "«include»" .-> AIAdvisor
```

| Actor | Description |
|-------|-------------|
| User | Người dùng tương tác với hệ thống qua giao diện web |
| System | AI Web Vulnerability Scanner (Flask app) |
| AI Module | Mô-đun LLM tư vấn cách khắc phục lỗ hổng |

| Use Case | Description |
|----------|-------------|
| Start Scan | Nhập URL, bắt đầu quét toàn bộ pipeline |
| Validate URL | Kiểm tra URL hợp lệ và có thể truy cập |
| Crawl Pages | Thu thập pages và forms từ target |
| Detect Vulnerabilities | Thử nghiệm SQLi và XSS payloads |
| AI Remediation Advisor | Phân tích lỗ hổng và đưa ra hướng dẫn khắc phục |
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
    participant AI as AI Advisor
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

        alt Vulnerability Found
            Scanner->>AI: get_remediation(vulnerability)
            AI-->>Scanner: remediation_json (Explanation, Fix, Code)
        else No Vulnerability
            Scanner-->>Scanner: skip AI
        end
    end

    Scanner->>DB: save_vulnerabilities()
    Scanner-->>Route: scan_id
    Route-->>UI: redirect /results/<scan_id>
    UI-->>User: Display results page
```

**Ghi chu:** Nhanh `alt/else` cho AI Advisor logic - neu tim thay lo hong, he thong gui evidence cho LLM de lay huong dan khac phuc.

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
    O -->|No| K
    N --> K
    P --> K
    K -->|No| Q{Vuln Found\nin Form?}
    Q -->|Yes| R[Send Data to\nAI Advisor]
    R --> S[Get Remediation\nJSON]
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
3. Moi form: thu SQLi -> thu XSS -> Goi AI Advisor neu tim thay lo hong
4. Luu ket qua -> hien thi trang results
