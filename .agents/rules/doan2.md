---
trigger: always_on
---

# ================================
# GLOBAL RULE: AI WEB VULNERABILITY SCANNER
# ================================

context:
  project_type: "Academic Project 2"
  domain: "Cybersecurity + Web Development + AI"
  goal: "Build AI-integrated Web Vulnerability Scanner"
  language: "Python"
  framework: "Flask"
  ai_lib: "scikit-learn"
  style: "Clean, modular, academic-ready"

# ================================
# CODING PRINCIPLES
# ================================

rules:
  - Always write clean, modular, and readable code
  - Follow separation of concerns (UI / Scanner / AI / DB)
  - Use meaningful variable and function names
  - Avoid hardcoding values
  - Prefer reusable functions over duplication
  - Add comments only when necessary (no over-commenting)
  - Code must be easy to explain in academic report

# ================================
# PROJECT ARCHITECTURE
# ================================

architecture:
  structure:
    - app/
    - app/routes/
    - app/services/
    - app/models/
    - app/utils/
    - templates/
    - static/

  modules:
    - Web Interface (Flask routes + HTML)
    - Crawler (link discovery + form extraction)
    - Scanner Engine (request + response handler)
    - Vulnerability Detection (SQLi, XSS)
    - AI Module (response classification)
    - Report Module (results + history)
    - Database (SQLite/MySQL)

# ================================
# WEB CRAWLER RULES
# ================================

crawler_rules:
  - Only crawl within same domain
  - Limit crawl depth (default: 2–3)
  - Avoid duplicate URLs
  - Extract:
      - links
      - forms
      - input fields
  - Ignore:
      - logout links
      - external domains
  - Use BeautifulSoup for parsing

# ================================
# VULNERABILITY DETECTION RULES
# ================================

detection_rules:

  sql_injection:
    payloads:
      - "' OR '1'='1"
      - "' OR 1=1--"
      - "'; DROP TABLE users--"
    indicators:
      - SQL error keywords (e.g., "syntax error", "mysql", "sql")
      - abnormal response length
      - different status code

  xss:
    payloads:
      - "<script>alert(1)</script>"
      - "\"><script>alert(1)</script>"
    indicators:
      - reflected payload in response
      - script execution patterns

  general:
    - Always compare baseline response vs test response
    - Store all test results for AI processing
    - Detection logic must remain simple (educational purpose)

# ================================
# AI MODULE RULES
# ================================

ai_rules:
  model: "LogisticRegression or RandomForest"
  type: "Supervised Learning"

  features:
    - response_length
    - status_code
    - keyword_presence
    - payload_reflection (true/false)

  preprocessing:
    - normalize numeric values
    - encode categorical data

  output:
    - classify: "normal" or "suspicious"

  constraints:
    - Keep model simple (prototype level)
    - Explainable output preferred
    - Do not overfit (small dataset expected)

# ================================
# DATABASE RULES
# ================================

database_rules:
  tables:
    - scans
    - pages
    - vulnerabilities
    - ai_results

  principles:
    - Keep schema simple
    - Ensure relationships are logical
    - Store scan history for later analysis

# ================================
# API & REQUEST HANDLING
# ================================

http_rules:
  - Use requests library
  - Handle:
      - GET and POST
      - headers
      - parameters
  - Add timeout for requests
  - Prevent infinite loops

# ================================
# REPORT GENERATION RULES
# ================================

report_rules:
  - Output must include:
      - URL scanned
      - vulnerabilities found
      - payload used
      - response behavior
      - AI classification
  - Format must be readable (table or structured JSON)
  - Store results in database

# ================================
# SECURITY & ETHICS
# ================================

security_rules:
  - Only test on authorized targets
  - Do not perform destructive attacks
  - No real exploitation beyond detection
  - Safe payloads only

# ================================
# UI RULES
# ================================

ui_rules:
  - Simple and clean interface
  - Required pages:
      - Home (input URL)
      - Scan results
      - History
  - Clear display of findings
  - Avoid complex frontend frameworks

# ================================
# DEVELOPMENT STRATEGY
# ================================

workflow:
  - Step 1: Build Flask UI
  - Step 2: Implement crawler
  - Step 3: Add detection module
  - Step 4: Integrate AI module
  - Step 5: Add database
  - Step 6: Generate reports

# ================================
# OUTPUT STYLE (VERY IMPORTANT)
# ================================

assistant_behavior:
  - Always generate production-like code (not pseudo)
  - Provide full working snippets
  - Keep explanations short unless asked
  - When possible, align code with report writing
  - Suggest improvements like Cursor AI

# ================================
# LIMITATIONS (FOR ACADEMIC ALIGNMENT)
# ================================

constraints:
  - Do NOT over-engineer
  - Do NOT use complex ML models (no deep learning)
  - Focus on clarity over performance
  - Prioritize explainability for report

# ================================
# END RULE
# ================================