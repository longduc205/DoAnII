# 🛡️ AI Web Vulnerability Scanner (Remediation Advisor)

An AI-integrated web vulnerability scanner that combines rule-based security testing (SQL Injection, XSS) with **Generative AI** to provide detailed remediation advice, impact analysis, and interactive Q&A.

This project is built as an academic cybersecurity prototype (Project 2 / Đồ án II) and is intended for educational and authorized security testing use only.

---

## 1) What this project does

The scanner performs an end-to-end workflow:

1. **Crawl**: Discover links, forms, and inputs on a target website.
2. **Detect**: Inject context-aware payloads to identify SQLi and XSS vulnerabilities.
3. **Analyze**: Use rule-based logic to confirm vulnerabilities from server responses.
4. **Remediate (AI)**: Send findings to an LLM (Blackbox AI / Gemini) to generate:
   - **Why?**: Reasoning for the detection and why it's dangerous.
   - **How to fix**: Step-by-step checklist for developers.
   - **Code Examples**: Comparison between vulnerable and secure code snippets.
5. **Interactive Q&A**: Chat with the AI about specific findings to clarify doubts.

---

## 2) Core features

- **Dynamic Remediation**: Get specific fix advice for every finding using Blackbox AI (DeepSeek-V3).
- **AI Chat Box**: Interactive Q&A panel for each vulnerability to help developers understand the risks.
- **Automated Discovery**: High-performance crawling and form mapping.
- **Precision Detection**: Rule-based engine with verified payload evidence.
- **Modern Dashboard**: Dashboard with overview stats, risk distribution, and scan history.
- **Dockerized**: Fully containerized environment for easy deployment.

---

## 3) Tech stack

- **Language:** Python 3.11+
- **Backend:** Flask, Jinja2
- **AI Integration:** Blackbox AI API (DeepSeek-V3), Google Gemini SDK
- **Database ORM:** Flask-SQLAlchemy (SQLite)
- **HTTP & Parsing:** requests, beautifulsoup4, lxml
- **Containerization:** Docker, Docker Compose

---

## 4) Project structure

```text
DoAnII/
├── app/                        # Flask application package
│   ├── __init__.py             # App factory & Global Context
│   ├── config.py               # Configuration & API Keys
│   ├── models/                 # DB Models (Scan, Vuln, AIResult)
│   ├── routes/                 # Web routes (main, scan, ai_chat, etc.)
│   ├── services/               # crawler, scanner, detector, ai_advisor
│   ├── static/                 # CSS/JS/icons
│   └── utils/                  # db init, logger, helpers
├── templates/                  # Jinja2 templates (Dashboard, Results, Chat)
├── tests/                      # Pytest suite
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Web app image definition
├── requirements.txt            # Python dependencies
└── run.py                      # App entrypoint
```

---

## 5) Quick start (Docker)

### 1. Prerequisites
- Docker & Docker Compose (v2+)
- An API Key (Blackbox AI or Google Gemini)

### 2. Configure API Key
Create/Edit the `.env` file in the root directory:
```bash
# Blackbox AI Configuration
BLACKBOX_API_KEY=your_blackbox_api_key_here
```

### 3. Run services
```bash
docker compose up --build
```

Access the UI at: `http://localhost:5000`

---

## 6) Configuration notes

- **AI Advisor**: Controlled via `BLACKBOX_API_KEY` in `.env`. If no key is provided, the system falls back to static remediation templates.
- **Target Target**: For local testing, use the included DVWA at `http://localhost:8080` (credentials: `admin/password`).

---

## 7) Usage guide

1. **Launch Scan**: Enter a target URL and select vulnerability types.
2. **View Results**: Click on a scan result to see discovered vulnerabilities.
3. **AI Insights**:
   - Check the **AI Remediation** panel for each finding.
   - Click **"Ask AI about this finding"** to open the chat interface.
4. **Interactive Chat**: Type your questions (e.g., "How to fix this in PHP?") and get instant expert advice.

---

## 8) Ethical and legal notice

This tool is for **educational and authorized testing only**.  
Do not scan systems you do not own or do not have explicit permission to test. The AI-generated advice should be verified by a professional before implementation.

---

## 9) License / usage context

Academic project use (Project 2 / Đồ án II).
