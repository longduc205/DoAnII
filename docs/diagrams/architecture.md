# System Architecture

> **Phase:** Phase 2 - System Architecture Design
> **Day:** Day 13
> **Generated:** 2026-04-29

---

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        Browser["Web Browser"]
    end

    subgraph WebLayer["Web Interface (Flask)"]
        UI["UI Templates\nJinja2 + HTML/CSS/JS"]
        Routes["Flask Routes\n(routes/)"]
    end

    subgraph ScannerEngine["Scanner Engine (services/)"]
        Crawler["Crawler\ncrawler.py"]
        Detector["Detector\ndetector.py"]
        Scanner["Scanner\nscanner.py"]
    end

    subgraph AIModule["AI Module (ai/)"]
        FeatureExtractor["Feature Extractor\nfeature_extractor.py"]
        Predictor["Predictor\npredictor.py"]
        Model["ML Model\nclassifier.pkl"]
    end

    subgraph DataLayer["Data Layer"]
        DB["SQLite Database\n(Flask-SQLAlchemy)"]
        Payloads["Payload Files\ndata/payloads/"]
    end

    Browser -->|"HTTP Request"| UI
    UI --> Routes
    Routes -->|"start_scan()"| Scanner
    Scanner --> Crawler
    Crawler -->|"pages, forms"| Detector
    Detector -->|"responses"| FeatureExtractor
    FeatureExtractor -->|"features"| Predictor
    Predictor --> Model
    Scanner -->|"vulnerabilities"| DB
    Scanner -->|"ai_results"| DB
    Crawler -.-> Payloads
    Detector -.-> Payloads
```

---

## 2. Module Descriptions

### 2.1 Web Interface Layer

| Module | File | Responsibility |
|--------|------|----------------|
| UI Templates | `templates/*.html` | Render pages using Jinja2: home, scan, results, history |
| Flask Routes | `app/routes/*.py` | Handle HTTP requests, call scanner engine, return responses |

**Routes:**

| Route | File | Description |
|-------|------|-------------|
| `/` | `main.py` | Home page - URL input form |
| `/scan` | `scan.py` | Start a new scan session |
| `/results/<id>` | `results.py` | Display scan results |
| `/history` | `history.py` | List past scan sessions |

### 2.2 Scanner Engine

| Module | File | Responsibility |
|--------|------|----------------|
| Scanner | `scanner.py` | Orchestrates the full pipeline: crawl → detect → AI → save |
| Crawler | `crawler.py` | Discover pages and forms from target URL |
| Detector | `detector.py` | Inject payloads and analyze responses for SQLi/XSS |

**Crawler (`crawler.py`) responsibilities:**
- BFS traversal from base URL
- Respect max depth (default: 3) and max pages (default: 50)
- Extract all `<a>` links and `<form>` elements
- Skip external domains, logout links, duplicate URLs
- Return list of `Page` objects with forms

**Detector (`detector.py`) responsibilities:**
- Send baseline request (normal parameters)
- Inject payloads from `data/payloads/sqli_payloads.txt` and `data/payloads/xss_payloads.txt`
- Compare test response vs baseline (length, status code, content)
- Detect SQL error keywords and XSS reflection patterns
- Return list of `Vulnerability` objects

### 2.3 AI Module

| Module | File | Responsibility |
|--------|------|----------------|
| Feature Extractor | `ai/feature_extractor.py` | Extract numeric features from HTTP responses |
| Predictor | `ai/predictor.py` | Load model and predict classification |
| Trainer | `ai/trainer.py` | Train and save the ML model |

**Feature set:**

| Feature | Type | Description |
|---------|------|-------------|
| `response_length` | Numeric | Length of HTTP response body |
| `status_code` | Numeric | HTTP status code (200, 500, etc.) |
| `keyword_presence` | Boolean | SQL error keywords found in response |
| `payload_reflection` | Boolean | XSS payload reflected in response |

**Model:** LogisticRegression (primary), RandomForest (comparison). Both trained via scikit-learn.

### 2.4 Data Layer

| Component | Description |
|-----------|-------------|
| SQLite Database | Persistent storage via Flask-SQLAlchemy |
| Models | `Scan`, `Page`, `Vulnerability`, `AIResult` |
| Payload Files | Plain-text files with detection payloads |

**Database Schema (ER Overview):**

```mermaid
erDiagram
    SCAN {
        int id PK
        string target_url
        string status
        datetime started_at
        datetime completed_at
        int total_pages
        int total_forms
        int total_vulnerabilities
    }
    PAGE {
        int id PK
        int scan_id FK
        string url
        string method
        string forms_json
    }
    VULNERABILITY {
        int id PK
        int scan_id FK
        string vuln_type
        string severity
        string url
        string parameter
        text payload
        text evidence
        datetime detected_at
    }
    AI_RESULT {
        int id PK
        int scan_id FK
        string classification
        float confidence
        json features
        datetime classified_at
    }
    SCAN ||--o{ PAGE : contains
    SCAN ||--o{ VULNERABILITY : contains
    SCAN ||--o{ AI_RESULT : contains
```

---

## 3. Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Flask as Flask Routes
    participant Scanner as Scanner Engine
    participant Crawler
    participant Detector
    participant AI as AI Module
    participant DB as Database

    User->>Flask: Submit target URL
    Flask->>Scanner: start_scan(target_url)

    Scanner->>Crawler: crawl(base_url)
    loop For each discovered page
        Crawler->>Crawler: fetch_page(url)
        Crawler->>Crawler: extract_forms(html)
    end
    Crawler-->>Scanner: pages[], forms[]

    Scanner->>DB: create_scan_session()

    loop For each form
        Scanner->>Detector: test_sqli(form)
        loop For each SQLi payload
            Detector->>Detector: send_request(payload)
            Detector->>Detector: compare_responses()
        end
        Detector-->>Scanner: sqli_findings[]

        Scanner->>Detector: test_xss(form)
        loop For each XSS payload
            Detector->>Detector: send_request(payload)
            Detector->>Detector: check_reflection()
        end
        Detector-->>Scanner: xss_findings[]

        Scanner->>AI: extract_features(response)
        AI-->>Scanner: features{}
        Scanner->>AI: predict(features)
        AI-->>Scanner: classification, confidence
        Scanner->>DB: save_ai_result()
    end

    Scanner->>DB: save_vulnerabilities()
    Scanner-->>Flask: scan_id
    Flask-->>User: Redirect to results page
```

---

## 4. Component Interaction Summary

```mermaid
flowchart LR
    subgraph Input
        URL["Target URL\nfrom User"]
    end

    subgraph Core
        Crawler["Crawler"]
        Detector["Detector"]
        AI["AI Module"]
    end

    subgraph Output
        Results["Results Page"]
        History["History Page"]
    end

    URL -->|Start Scan| Crawler
    Crawler -->|pages + forms| Detector
    Detector -->|responses| AI
    AI -->|classification| Results
    Detector -->|vulnerabilities| Results
    Results --> History

    style URL fill:#e1f5fe
    style Results fill:#f1f8e9
    style History fill:#fff3e0
    style Crawler fill:#f3e5f5
    style Detector fill:#fce4ec
    style AI fill:#e8f5e9
```

| Interaction | Description |
|-------------|-------------|
| URL → Crawler | User submits URL; crawler starts BFS from it |
| Crawler → Detector | Crawler passes discovered forms to detector for testing |
| Detector → AI | Detector sends responses to AI for classification |
| Detector → Results | Vulnerabilities saved and displayed |
| AI → Results | AI classifications saved and displayed |

---

## 5. File-to-Module Mapping

| File Path | Role |
|-----------|------|
| `app/routes/main.py` | Home page route |
| `app/routes/scan.py` | Start scan route |
| `app/routes/results.py` | Display results route |
| `app/routes/history.py` | Display history route |
| `app/services/scanner.py` | Pipeline orchestrator |
| `app/services/crawler.py` | Page & form discovery |
| `app/services/detector.py` | SQLi & XSS testing |
| `app/services/ai_analyzer.py` | AI analysis integration |
| `ai/feature_extractor.py` | Feature extraction |
| `ai/predictor.py` | Model prediction |
| `ai/trainer.py` | Model training |
| `app/models/scan.py` | Scan session model |
| `app/models/page.py` | Page model |
| `app/models/vulnerability.py` | Vulnerability model |
| `app/models/ai_result.py` | AI result model |
| `data/payloads/sqli_payloads.txt` | SQLi payloads |
| `data/payloads/xss_payloads.txt` | XSS payloads |
| `templates/*.html` | UI templates |
| `app/static/css/style.css` | Styles |
| `app/static/js/main.js` | Frontend JS |
