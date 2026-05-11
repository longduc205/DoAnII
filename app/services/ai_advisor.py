"""
AI Advisor Service

Uses Google Gemini API to generate remediation recommendations
and answer user questions about vulnerability findings.

When no API key is configured, falls back to a built-in
template-based remediation system.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static fallback remediation templates (used when Gemini is unavailable)
# ---------------------------------------------------------------------------

_FALLBACK_REMEDIATIONS = {
    'sqli': {
        'explanation': (
            'The scanner injected a SQL payload into the form parameter and '
            'observed a significant change in the server response compared '
            'to the baseline.  This indicates the input was interpreted as '
            'SQL code rather than plain text — meaning the application '
            'builds SQL queries by concatenating user input without '
            'sanitisation.'
        ),
        'remediation_steps': [
            'Use parameterised queries (prepared statements) instead of string concatenation.',
            'Apply input validation — reject unexpected characters such as single quotes.',
            'Use an ORM (e.g. SQLAlchemy, Sequelize) which escapes parameters automatically.',
            'Apply the principle of least privilege to the database account used by the app.',
            'Deploy a Web Application Firewall (WAF) as an additional layer of defence.',
        ],
        'code_example': (
            "# VULNERABLE — never do this:\n"
            "cursor.execute(f\"SELECT * FROM users WHERE name = '{user_input}'\")\n"
            "\n"
            "# SAFE — use parameterised queries:\n"
            "cursor.execute(\"SELECT * FROM users WHERE name = %s\", (user_input,))"
        ),
    },
    'xss': {
        'explanation': (
            'The scanner injected an XSS payload into the form parameter '
            'and found the payload reflected verbatim (unencoded) in the '
            'server response.  This means the application does not sanitise '
            'or escape user-supplied input before rendering it in HTML, '
            'allowing an attacker to inject arbitrary JavaScript.'
        ),
        'remediation_steps': [
            'Encode all user-supplied output using context-appropriate encoding (HTML, JS, URL).',
            'Use a templating engine that auto-escapes by default (Jinja2, React JSX).',
            'Implement a Content Security Policy (CSP) header to block inline scripts.',
            'Validate and sanitise input on the server side — reject or strip HTML tags.',
            'Use HTTPOnly and Secure flags on cookies to limit script access.',
        ],
        'code_example': (
            "<!-- VULNERABLE — never do this: -->\n"
            "<p>Hello {{ user_input | safe }}</p>\n"
            "\n"
            "<!-- SAFE — let Jinja2 auto-escape (default): -->\n"
            "<p>Hello {{ user_input }}</p>\n"
            "\n"
            "<!-- Or escape explicitly: -->\n"
            "<p>Hello {{ user_input | e }}</p>"
        ),
    },
}

_DEFAULT_FALLBACK = {
    'explanation': (
        'The scanner detected an anomalous response when injecting a test '
        'payload into this parameter, suggesting the input is not properly '
        'validated or sanitised.'
    ),
    'remediation_steps': [
        'Review the finding details and evidence.',
        'Apply appropriate input validation and output encoding.',
        'Follow OWASP guidelines for the specific vulnerability type.',
    ],
    'code_example': '',
}


class AIAdvisor:
    """AI advisor using Blackbox.ai API with static fallback."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('BLACKBOX_API_KEY', '') or 'sk-4Qk5OHr9GYuUGAuuMxcNiQ'
        self.api_url = "https://api.blackbox.ai/v1/chat/completions"
        logger.info('Blackbox AI advisor initialised (key: %s...)', self.api_key[:8])

    def is_available(self):
        """Check if we have an API key or at least the service is intended to be used."""
        return bool(self.api_key) or os.getenv('USE_BLACKBOX', 'false').lower() == 'true'

    def get_remediation(self, vuln_type, severity, url, parameter, payload, evidence):
        if not self.is_available():
            return self._get_fallback(vuln_type)

        try:
            vuln_label = 'SQL Injection' if vuln_type == 'sqli' else \
                         'Cross-Site Scripting (XSS)' if vuln_type == 'xss' else vuln_type.upper()

            prompt = f"""You are a web security expert. A scanner detected {vuln_label} at {url} on parameter '{parameter}'.
Payload: {payload}
Evidence: {evidence}

Respond with ONLY a JSON object:
{{
  "explanation": "Why this was detected and why it is dangerous (3-4 sentences)",
  "remediation_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
  "code_example": "Vulnerable vs Secure code snippet"
}}"""
            return self._call_blackbox(prompt, is_json=True)
        except Exception as exc:
            logger.error('Blackbox remediation failed: %s', exc)
            return self._get_fallback(vuln_type)

    def ask_question(self, question, finding_context=None):
        if not self.is_available():
            return "AI advisor (Blackbox) is not configured. Please add BLACKBOX_API_KEY to .env."

        ctx = ""
        if finding_context:
            ctx = f"Context: {finding_context['vuln_type']} at {finding_context['url']} on param {finding_context['parameter']}.\n"
        
        prompt = f"{ctx}User question: {question}\nRespond concisely as a security expert."
        try:
            return self._call_blackbox(prompt, is_json=False)
        except Exception as exc:
            return f"Blackbox AI error: {str(exc)}"

    def _call_blackbox(self, prompt, is_json=False):
        """Helper to call Blackbox AI API with standard OpenAI format."""
        import requests
        import json
        
        api_key = self.api_key

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "blackboxai/x-ai/grok-code-fast-1:free",
            "max_tokens": 1024,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            print(f"\n[DEBUG] Calling Blackbox with key: {api_key[:8]}...")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            print(f"[DEBUG] Status: {response.status_code}")
            raw_text = response.text
            print(f"[DEBUG] Raw Response: {raw_text[:200]}...")

            if response.status_code != 200:
                return f"AI Error {response.status_code}: {raw_text[:50]}"

            # Handle SSE style response (data: {"choices": ...})
            content = ""
            if raw_text.startswith("data: "):
                # Extract content from the first data line that has choices
                for line in raw_text.split("\n"):
                    if line.startswith("data: ") and "choices" in line:
                        try:
                            line_data = json.loads(line[6:])
                            content = line_data['choices'][0]['message']['content']
                            break
                        except: continue
                if not content: content = raw_text # Fallback
            else:
                try:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                except:
                    content = raw_text

            if is_json:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                try:
                    return json.loads(content)
                except:
                    return self._get_fallback("sqli")
            
            return content
        except Exception as exc:
            print(f"[DEBUG] Exception: {str(exc)}")
            return f"AI Connection Error: {str(exc)}"

    # -----------------------------------------------------------------
    # Fallback
    # -----------------------------------------------------------------

    def _get_fallback(self, vuln_type):
        """Return a static remediation template."""
        return dict(_FALLBACK_REMEDIATIONS.get(vuln_type, _DEFAULT_FALLBACK))
