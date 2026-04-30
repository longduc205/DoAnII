# ER Diagram - AI Web Vulnerability Scanner

> **Phase:** Phase 2 - System Design
> **Day:** Day 15
> **Database:** SQLite with Flask-SQLAlchemy

---

## ER Diagram

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
        int status_code
        int depth
        bool has_forms
        int form_count
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
        string url
        string classification
        float confidence
        int response_length
        int status_code
        bool has_reflection
        bool has_error_keywords
        datetime classified_at
    }

    SCAN ||--o{ PAGE : contains
    SCAN ||--o{ VULNERABILITY : contains
    SCAN ||--o{ AI_RESULT : contains
```

---

## Relationships

| Parent | Child | Type | Cascade |
|--------|-------|------|---------|
| SCAN | PAGE | One-to-Many | ON DELETE CASCADE |
| SCAN | VULNERABILITY | One-to-Many | ON DELETE CASCADE |
| SCAN | AI_RESULT | One-to-Many | ON DELETE CASCADE |

**ER Diagram (cu phap cuc bo):**

```
SCAN (1) ──┬── (N) PAGE
           ├── (N) VULNERABILITY
           └── (N) AI_RESULT
```

Moi SCAN chua nhieu PAGE, VULNERABILITY, AI_RESULT. Khi xoa SCAN, tat ca cac bang con deu bi xoa tu dong (cascade delete).
