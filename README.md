# 🛡️ AI Web Vulnerability Scanner

An AI-integrated web vulnerability scanner that combines rule-based security testing (SQL Injection, XSS) with machine-learning-assisted HTTP response classification.

This project is built as an academic cybersecurity prototype (Project 2 / Đồ án II) and is intended for educational and authorized security testing use only.

---

## 1) What this project does

The scanner performs an end-to-end workflow:

1. Crawl a target website and collect links/forms.
2. Inject SQLi/XSS payloads into discovered inputs.
3. Analyze HTTP responses using rule-based detectors.
4. Classify responses with an ML model (normal vs suspicious).
5. Store and display findings in a web dashboard.

---

## 2) Core features

- Flask web UI for launching scans and reviewing results
- Automated crawling and form/input discovery
- SQL Injection and XSS payload-based testing
- AI response analysis module (scikit-learn)
- Scan history and result persistence (SQLAlchemy ORM)
- Dockerized development workflow (with optional DVWA target)

---

## 3) Tech stack

- **Language:** Python 3.9+
- **Backend:** Flask, Jinja2
- **Database ORM:** Flask-SQLAlchemy
- **HTTP & Parsing:** requests, beautifulsoup4, lxml
- **AI/ML:** scikit-learn, numpy, pandas, joblib
- **Testing:** pytest, pytest-cov, hypothesis
- **Containerization:** Docker, Docker Compose

---

## 4) Project structure

```text
DoAnII/
├── app/                        # Flask application package
│   ├── __init__.py             # App factory (create_app)
│   ├── config.py               # Configuration
│   ├── models/                 # SQLAlchemy models
│   ├── routes/                 # Web routes (main, scan, results, history, tasks)
│   ├── services/               # crawler, scanner, detector, ai_analyzer
│   ├── static/                 # CSS/JS/icons
│   └── utils/                  # db init, logger, helpers, http client
├── ai/                         # Feature extraction, preprocessing, trainer, predictor
├── data/                       # payloads + raw/processed datasets
├── docs/                       # diagrams, screenshots, references
├── scripts/                    # training-data, model training, validation, utilities
├── templates/                  # Jinja templates
├── tests/                      # test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run.py                      # app entrypoint
└── README.md
```

---

## 5) Quick start (Docker recommended)

### Prerequisites

- Docker
- Docker Compose (v2+)

### Run services

```bash
docker compose up --build
```

This starts:

- **web app** at `http://localhost:5000`
- **DVWA target** at `http://localhost:8080`

Stop services:

```bash
docker compose down
```

---

## 6) Local development setup (without Docker)

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

Open: `http://localhost:5000`

### Optional: initialize database explicitly

```bash
python3 -m app.utils.db_init
```

---

## 7) Configuration notes

Configuration is defined in `app/config.py` and environment variables.

Common variables used by the app include:

- `SECRET_KEY`
- `DATABASE_URL` (default SQLite)
- `AI_MODEL_PATH` (default: `ai/models/classifier.pkl`)
- `AI_CONFIDENCE_THRESHOLD`

For Docker, `docker-compose.yml` loads variables from `.env` if present.  
If you do not provide `.env`, defaults from config are used where applicable.

---

## 8) Usage guide (onboarding flow)

1. Start the app (`docker compose up --build` or `python3 run.py`).
2. Open the UI at `http://localhost:5000`.
3. Go to the scan page.
4. Enter a target URL (for local testing, you can use DVWA at `http://dvwa` from inside Docker network, or `http://localhost:8080` from host-side workflows as applicable).
5. Launch scan and wait for processing.
6. Review findings in the results page.
7. Browse previous sessions in history/tasks pages.

---

## 9) AI model workflow

If model artifacts are missing or you want retraining:

### Generate synthetic training data

```bash
python3 scripts/generate_training_data.py
```

### (Optional) Collect real data from DB

```bash
python3 scripts/collect_db_data.py
```

### Merge datasets

```bash
python3 scripts/merge_datasets.py
```

### Train model

```bash
python3 scripts/train_model.py
```

Expected output artifacts are saved under `ai/models/` (for example `classifier.pkl`, scaler files depending on trainer config).

---

## 10) Running tests

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest --cov=app --cov=ai tests/ -v
```

---

## 11) Troubleshooting

- **Port 5000 already in use**  
  Stop conflicting process or map a different host port in `docker-compose.yml`.

- **Model not found / AI not ready**  
  Run training scripts and ensure `AI_MODEL_PATH` points to an existing model file.

- **Dependency installation issues**  
  Recreate virtual env:
  ```bash
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- **Database issues**  
  Reinitialize DB with:
  ```bash
  python3 -m app.utils.db_init
  ```

---

## 12) Ethical and legal notice

This tool is for **educational and authorized testing only**.  
Do not scan systems you do not own or do not have explicit permission to test.

---

## 13) License / usage context

Academic project use (Project 2 / Đồ án II).
