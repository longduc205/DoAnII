# AI Web Vulnerability Scanner - Requirements Specification

> **Project:** AI Web Vulnerability Scanner
> **Phase:** Phase 2 - Requirement Analysis & System Design
> **Days:** Day 11-12
> **Status:** Draft

---

## 1. Project Overview

**AI Web Vulnerability Scanner** is a web application that automatically detects SQL Injection (SQLi) and Cross-Site Scripting (XSS) vulnerabilities in target websites, using both rule-based detection and AI-powered response classification.

The system crawls a target website, extracts forms, injects test payloads, analyzes server responses, and utilizes Generative AI (LLMs like Gemini and Blackbox) to provide detailed remediation advice and interactive Q&A for any discovered findings. Scan results and AI insights are stored and displayed through a modern Flask-based web interface.

**Target Users:** Security researchers, developers, students learning web security.

---

## 2. Functional Requirements

### FR1: Target URL Input

**Description:** The system must accept a target URL from the user via the web interface.

**Input:** A valid HTTP/HTTPS URL (e.g., `http://example.com`).

**Output:** URL is validated and stored as the scan target. The system confirms the URL is reachable before proceeding.

**Priority:** Critical

**Acceptance Criteria:**
- [x] User can enter URL in input field on the home page
- [x] System validates URL format before accepting
- [x] System checks URL reachability before starting scan
- [x] Error message displayed if URL is invalid or unreachable

---

### FR2: Web Crawling & Page Discovery

**Description:** The system must crawl the target website and discover all accessible pages and forms.

**Input:** Base URL of target website.

**Output:** A list of discovered pages and forms with input fields.

**Priority:** Critical

**Acceptance Criteria:**
- [x] Crawler starts from the base URL provided by user
- [x] Crawler discovers all internal links within the same domain
- [x] Crawler respects a configurable maximum depth (default: 3)
- [x] Crawler respects a configurable maximum page limit (default: 50)
- [x] Crawler extracts all forms from each discovered page
- [x] Crawler extracts all input fields from each form (text, password, search, textarea, etc.)
- [x] Crawler skips external domains, logout links, and anchor-only links
- [x] Duplicate URLs are ignored
- [x] Scan session metadata is saved to database (total pages, total forms)

---

### FR3: SQL Injection Detection

**Description:** The system must test each discovered form for SQL Injection vulnerabilities.

**Input:** Form data including action URL, method (GET/POST), and parameters.

**Output:** List of confirmed or suspected SQLi vulnerabilities.

**Priority:** Critical

**Acceptance Criteria:**
- [x] System sends a baseline request (normal parameters) and records response
- [x] System sends test requests with SQLi payloads for each form parameter
- [x] Payloads include: `' OR '1'='1`, `' OR 1=1--`, `'; DROP TABLE users--`, and others from `data/payloads/sqli_payloads.txt`
- [x] System detects SQLi by comparing baseline vs test responses:
  - SQL error keywords in response body (e.g., "syntax error", "mysql", "sql")
  - Abnormal response length change
  - HTTP status code change
- [x] Each finding is stored with: URL, parameter, payload used, evidence snippet
- [x] Findings are associated with the current scan session in the database

---

### FR4: Cross-Site Scripting (XSS) Detection

**Description:** The system must test each discovered form for Reflected XSS vulnerabilities.

**Input:** Form data including action URL, method (GET/POST), and parameters.

**Output:** List of confirmed or suspected XSS vulnerabilities.

**Priority:** Critical

**Acceptance Criteria:**
- [x] System sends test requests with XSS payloads for each form parameter
- [x] Payloads include: `<script>alert(1)</script>`, `"><script>alert(1)</script>`, and others from `data/payloads/xss_payloads.txt`
- [x] System detects XSS by checking if payload is reflected in the response body
- [x] System checks for script tag injection patterns in response
- [x] Each finding is stored with: URL, parameter, payload used, evidence snippet
- [x] Findings are associated with the current scan session in the database

---

### FR5: Generative AI Remediation Advisor & Interactive Chat

**Description:** The system must use Large Language Models (LLMs) to analyze discovered vulnerabilities, provide detailed remediation steps, and allow users to ask follow-up questions via a chat interface.

**Input:** Vulnerability details (type, payload, URL, evidence snippet) and user chat messages.

**Output:** Structured JSON response (Explanation, Remediation Steps, Code Example) and chat responses.

**Priority:** High

**Acceptance Criteria:**
- [x] System integrates with multiple LLM providers (Google Gemini & Blackbox AI).
- [x] System sends vulnerability evidence to the AI using structured prompt engineering.
- [x] AI returns a structured JSON containing:
  - `explanation`: Why the vulnerability exists.
  - `remediation`: Step-by-step guide to fix it.
  - `code_example`: Secure code snippet.
- [x] Web interface provides an interactive Chat Q&A panel on the results page.
- [x] Users can ask context-aware questions about the findings.
- [x] AI analysis results are saved in the `ai_results` table.
- [x] Fallback mechanisms exist in case the LLM API is unavailable.

---

### FR6: Scan Result Reporting

**Description:** The system must display detailed scan results through the web interface.

**Input:** Scan session ID.

**Output:** Human-readable report showing all vulnerabilities found and AI classifications.

**Priority:** High

**Acceptance Criteria:**
- [x] Results page shows scan summary: target URL, start time, end time, total pages, total forms, total vulnerabilities
- [x] Results page lists all detected vulnerabilities grouped by type (SQLi, XSS)
- [x] Each vulnerability entry shows: type, URL, parameter, payload, severity, evidence
- [x] Results page displays the AI-generated Explanation, Remediation Steps, and Code Example for each finding.
- [x] Interactive chat interface is available to query the AI advisor.
- [x] Results are retrieved from database and displayed in a modern, structured format (cards).
- [x] Results are accessible via a unique URL per scan session

---

### FR7: Scan History Management

**Description:** The system must maintain a history of all past scan sessions and allow users to review them.

**Input:** None (retrieves all records from database).

**Output:** List of past scan sessions with metadata, linkable to detailed results.

**Priority:** Medium

**Acceptance Criteria:**
- [x] History page lists all past scans ordered by date (newest first)
- [x] Each history entry shows: scan ID, target URL, status, start time, vulnerability count
- [x] User can click on a history entry to view full results
- [x] Scan sessions persist in the database across application restarts

---

## 3. Non-Functional Requirements

### 3.1 Usability

- The web interface must be simple and intuitive, requiring no technical expertise beyond basic web browsing.
- All UI text must be clear, with appropriate labels and placeholder values.
- The system must provide clear feedback during scanning (progress, current page being scanned, errors).
- Error messages must be human-readable and actionable.

### 3.2 Performance

- Single-page scans should complete within a reasonable time, depending on target site size.
- The crawler must respect a configurable delay between requests (default: 0.5s) to avoid overwhelming the target.
- HTTP requests must have a configurable timeout (default: 10 seconds).
- The system must handle unresponsive pages gracefully (skip and continue).

### 3.3 Security

- The system must only scan URLs within the same domain (no external link crawling).
- The system must not perform destructive operations (e.g., DROP TABLE) on the target server.
- All payloads used are safe detection payloads that do not cause permanent damage.
- The system must not store sensitive data from the target application.

### 3.4 Modularity & Maintainability

- The system must be modular: Crawler, Detector, AI Module, and Report Module are separate components.
- Each module must have a clear, documented interface.
- Code must follow clean architecture principles with separation of concerns.
- The system must use configuration files (`.env`) for all tunable parameters.

### 3.5 Scalability

- The crawler limit (max pages, max depth) must be configurable so the system can adapt to different target sizes.
- The database schema must support future extensions (additional vulnerability types, new AI models).
- New LLM providers can be added seamlessly by implementing the provider interface.

---

## 4. Use Case Summary

### Actor

| Actor | Description |
|-------|-------------|
| **User** | Security researcher, developer, or student who initiates scans and reviews results |

### Use Cases

| ID | Use Case | Description |
|----|----------|-------------|
| **UC1** | Start Scan | User enters target URL and clicks "Start Scan". System validates URL and begins crawling. |
| **UC2** | View Results | User views the scan results page showing all detected vulnerabilities and AI remediation advice. |
| **UC3** | View History | User navigates to the history page to see all past scan sessions. |
| **UC4** | View Scan Details | User clicks on a history entry to view the full results of a past scan. |

### Use Case Diagram

```
                    ┌─────────────────────────┐
                    │  AI Web Vulnerability   │
                    │        Scanner          │
                    └─────────────────────────┘
                                    │
                                    │──────────────┐
                                    │              │
                              ┌─────▼─────┐ ┌────▼────┐
                              │   User    │ │  AI     │
                              └─────┬─────┘ │ Module  │
                                    │       └─────────┘
                        ┌───────────┼───────────┐
                        │           │           │
                  ┌─────▼────┐ ┌────▼────┐ ┌────▼─────┐
                  │Start Scan│ │View      │ │View      │
                  │ (UC1)    │ │Results   │ │History   │
                  └──────────┘ │ (UC2)    │ │ (UC3)    │
                                └────┬─────┘ └──────────┘
                                     │
                               ┌─────▼──────┐
                               │View Scan   │
                               │Details(UC4)│
                               └────────────┘
```

### Data Flow Summary

```
User Input (URL)
       │
       ▼
  ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐
  │ Crawler │───▶│ Detector │───▶│AI Advisor │───▶│ Report  │
  └─────────┘    └──────────┘    └───────────┘    └─────────┘
       │              │                 │                 │
       ▼              ▼                 ▼                 ▼
   Pages DB     Vulnerabilities    AI Results        Results
                 DB Table           DB Table           Page
```

---

## 5. Acceptance Criteria Summary

| ID | Criteria | Priority |
|----|----------|----------|
| AC1 | User can enter and submit a target URL | Critical |
| AC2 | Crawler discovers pages and forms within configured limits | Critical |
| AC3 | SQLi detection identifies vulnerabilities using baseline comparison | Critical |
| AC4 | XSS detection identifies reflected payloads in responses | Critical |
| AC5 | Generative AI provides structured remediation advice for findings | High |
| AC6 | Interactive Chat Q&A functions correctly with scan context | High |
| AC7 | Results are displayed clearly with evidence | High |
| AC8 | Scan history persists across sessions | Medium |

---

> **Note:** This document is a living specification. Update as the system evolves during implementation.
