# 🛡️ AI Web Vulnerability Scanner

> An AI-integrated web vulnerability scanner that combines rule-based testing with machine-learning-assisted response classification. Built as an academic prototype for Project 2.

## 📋 Overview

This project implements a web vulnerability scanner with artificial intelligence support for response classification. The scanner crawls target web applications, identifies forms and input parameters, performs automated vulnerability tests (SQL Injection, XSS), and uses a trained ML model to classify server responses as normal or suspicious.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Web Interface                      │
│              (Flask + Jinja2 Templates)              │
├─────────────────────────────────────────────────────┤
│                    Flask Routes                      │
│         /scan  /results  /history  /report           │
├──────────┬──────────┬───────────┬───────────────────┤
│ Crawler  │ Scanner  │ AI Module │ Report Generator  │
│ Service  │ Engine   │           │                   │
├──────────┴──────────┴───────────┴───────────────────┤
│                  Database Layer                       │
│               (SQLite / MySQL)                       │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd DoAnII

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m app.utils.db_init

# Run the application
python run.py
```

### Access
Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
DoAnII/
├── app/                        # Main application package
│   ├── __init__.py             # Flask app factory
│   ├── config.py               # Configuration settings
│   ├── routes/                 # Route handlers (Blueprints)
│   │   ├── __init__.py
│   │   ├── main.py             # Home page routes
│   │   ├── scan.py             # Scan initiation & management
│   │   ├── results.py          # Results display
│   │   └── history.py          # Scan history
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── crawler.py          # Web crawler service
│   │   ├── scanner.py          # Scanner engine (orchestrator)
│   │   ├── detector.py         # Vulnerability detection logic
│   │   └── ai_analyzer.py      # AI classification service
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── scan.py             # Scan session model
│   │   ├── page.py             # Discovered page model
│   │   ├── vulnerability.py    # Vulnerability finding model
│   │   └── ai_result.py        # AI classification result model
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── db_init.py          # Database initialization
│   │   ├── http_client.py      # HTTP request wrapper
│   │   ├── logger.py           # Logging configuration
│   │   └── helpers.py          # General helper functions
│   └── static/                 # Static assets
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── icons/
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout template
│   ├── index.html              # Home page
│   ├── scan.html               # Scan page
│   ├── results.html            # Results page
│   └── history.html            # History page
├── ai/                         # AI/ML module
│   ├── __init__.py
│   ├── feature_extractor.py    # Feature extraction from responses
│   ├── preprocessor.py         # Data preprocessing pipeline
│   ├── trainer.py              # Model training script
│   ├── predictor.py            # Prediction/inference logic
│   └── models/                 # Saved ML models
│       └── .gitkeep
├── data/                       # Training data & datasets
│   ├── raw/                    # Raw collected data
│   │   └── .gitkeep
│   ├── processed/              # Processed/cleaned data
│   │   └── .gitkeep
│   └── payloads/               # Attack payload collections
│       ├── sqli_payloads.txt
│       └── xss_payloads.txt
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_crawler.py
│   ├── test_detector.py
│   ├── test_scanner.py
│   └── test_ai_analyzer.py
├── docs/                       # Documentation & report materials
│   ├── diagrams/               # UML & architecture diagrams
│   │   └── .gitkeep
│   ├── screenshots/            # UI screenshots for report
│   │   └── .gitkeep
│   └── references/             # Reference materials
│       └── .gitkeep
├── .gitignore
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
├── README.md                   # This file
└── TASKS.md                    # Development task breakdown
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Web Framework | Flask |
| Template Engine | Jinja2 |
| HTTP Client | Requests |
| HTML Parser | BeautifulSoup4 |
| AI/ML | Scikit-learn |
| Database | SQLite (dev) / MySQL (prod) |
| ORM | SQLAlchemy |

## ⚠️ Ethical Notice

This tool is designed for **educational purposes only**. Only scan web applications that you own or have explicit authorization to test. Unauthorized scanning is illegal and unethical.

## 📄 License

Academic Use - Project 2