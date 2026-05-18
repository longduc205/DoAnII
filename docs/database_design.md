# Database Design - AI Web Vulnerability Scanner

> **Phase:** Phase 2 - System Design
> **Day:** Day 15
> **Database:** SQLite with Flask-SQLAlchemy

---

## 1. Schema Overview

### Table: scans

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Scan session ID |
| target_url | VARCHAR(500) | NOT NULL | Target URL being scanned |
| status | VARCHAR(20) | DEFAULT 'pending' | pending / running / completed / failed |
| started_at | DATETIME | DEFAULT NOW | Scan start timestamp |
| completed_at | DATETIME | NULL | Scan completion timestamp |
| total_pages | INTEGER | DEFAULT 0 | Number of pages crawled |
| total_forms | INTEGER | DEFAULT 0 | Number of forms found |
| total_vulnerabilities | INTEGER | DEFAULT 0 | Number of vulnerabilities found |

**Indexes:** `idx_scans_status` on (status), `idx_scans_started_at` on (started_at)

---

### Table: pages

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Page ID |
| scan_id | INTEGER | FK -> scans.id, NOT NULL | Parent scan session |
| url | VARCHAR(500) | NOT NULL | Discovered page URL |
| status_code | INTEGER | NULL | HTTP status code |
| depth | INTEGER | DEFAULT 0 | Crawl depth (0 = root) |
| has_forms | BOOLEAN | DEFAULT FALSE | Whether page has forms |
| form_count | INTEGER | DEFAULT 0 | Number of forms on page |

**Indexes:** `idx_pages_scan_id` on (scan_id), `idx_pages_url` on (url)

---

### Table: vulnerabilities

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Vulnerability ID |
| scan_id | INTEGER | FK -> scans.id, NOT NULL | Parent scan session |
| vuln_type | VARCHAR(50) | NOT NULL | sqli / xss |
| severity | VARCHAR(20) | DEFAULT 'medium' | low / medium / high / critical |
| url | VARCHAR(500) | NOT NULL | Vulnerable page URL |
| parameter | VARCHAR(200) | NULL | Vulnerable parameter name |
| payload | TEXT | NULL | Payload that triggered detection |
| evidence | TEXT | NULL | Response snippet showing vulnerability |
| detected_at | DATETIME | DEFAULT NOW | Detection timestamp |

**Indexes:** `idx_vulns_scan_id` on (scan_id), `idx_vulns_type` on (vuln_type)

---

### Table: ai_results

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | AI result ID |
| scan_id | INTEGER | FK -> scans.id, NOT NULL | Parent scan session |
| url | VARCHAR(500) | NOT NULL | Vulnerability URL |
| explanation | TEXT | NULL | AI explanation of the vulnerability |
| remediation | TEXT | NULL | Step-by-step fix instructions |
| code_example | TEXT | NULL | Secure code snippet |
| created_at | DATETIME | DEFAULT NOW | Creation timestamp |

**Indexes:** `idx_ai_scan_id` on (scan_id)

---

## 2. Integrity Constraints

- **ON DELETE CASCADE:** Khi xoa scan, tat ca pages/vulnerabilities/ai_results cua scan do deu bi xoa tu dong
- **NOT NULL:** target_url (scans), scan_id (tat ca bang con), vuln_type (vulnerabilities), url (tat ca bang)
- **DEFAULT:** status='pending', severity='medium', has_forms=FALSE

---

## 3. Migration Strategy

Su dung Flask-Migrate (Alembic) de quan ly migration:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 4. Seed Data

Khong can seed data. Du lieu tu dong tao khi nguoi dung chay scan.

---

## 5. Code Implementation

Xem `app/models/scan.py`, `app/models/page.py`, `app/models/vulnerability.py`, `app/models/ai_result.py`.

Cac model da duoc implement san trong `app/models/`. Kiem tra:
- Tat ca columns deu khop voi schema
- Foreign key tu bang con den scans.id
- Cascade delete tren tat ca relationships
