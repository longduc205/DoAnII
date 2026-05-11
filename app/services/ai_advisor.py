"""
AI Advisor Service (Multi-Provider)
Supports: Blackbox AI & Google Gemini (via SDK)
"""

import json
import logging
import os
import requests
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AIAdvisor:
    def __init__(self, provider=None, api_key=None):
        self.provider = provider or os.getenv('AI_PROVIDER', 'blackbox').lower()
        
        if self.provider == 'gemini':
            self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
            if self.api_key:
                genai.configure(api_key=self.api_key)
                # Using gemini-flash-latest as discovered in model list
                self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.api_key = api_key or os.getenv('BLACKBOX_API_KEY', '')
            self.api_url = "https://api.blackbox.ai/v1/chat/completions"

    def is_available(self):
        return bool(self.api_key) and "your_gemini_api_key" not in self.api_key

    def get_model_name(self):
        if self.provider == 'gemini':
            return "Google Gemini (Latest)"
        return "Blackbox (DeepSeek-V3)"

    def get_remediation(self, vuln_type, severity, url, parameter, payload, evidence):
        prompt = self._build_remediation_prompt(vuln_type, severity, url, parameter, payload, evidence)
        return self._ask_ai(prompt, is_json=True)

    def ask_question(self, question, finding_context=None):
        ctx_str = ""
        if finding_context:
            ctx_str = (
                f"THE CONTEXT:\n"
                f"- Vulnerability: {finding_context['vuln_type']}\n"
                f"- Location: {finding_context['url']}\n"
                f"- Parameter: {finding_context['parameter']}\n"
                f"- Payload used: {finding_context['payload']}\n"
                "-------------------\n"
            )
        
        prompt = (
            f"You are a helpful Security Consultant. {ctx_str}"
            f"USER QUESTION: {question}\n\n"
            "INSTRUCTION: Provide a direct, specific answer to the user's question based on the context above. "
            "Be conversational and technical. Answer in the same language as the question if possible."
        )
        return self._ask_ai(prompt, is_json=False)

    def _ask_ai(self, prompt, is_json=False):
        if not self.is_available():
            err_msg = f"API Key for {self.provider} is missing or invalid in .env"
            return {"explanation": err_msg, "remediation_steps": [], "code_example": ""} if is_json else err_msg

        try:
            if self.provider == 'gemini':
                return self._call_gemini_sdk(prompt, is_json)
            else:
                return self._call_blackbox(prompt, is_json)
        except Exception as e:
            logger.error(f"AI Call failed ({self.provider}): {e}")
            return f"Error ({self.provider}): {str(e)}"

    def _call_blackbox(self, prompt, is_json=False):
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "blackboxai/x-ai/grok-code-fast-1:free",
            "max_tokens": 1024,
            "stream": False
        }
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            return f"Blackbox Error {resp.status_code}"
        
        content = self._parse_blackbox_response(resp.text)
        return self._process_content(content, is_json)

    def _call_gemini_sdk(self, prompt, is_json=False):
        # Using official SDK for better reliability
        generation_config = {}
        if is_json:
            generation_config = {"response_mime_type": "application/json"}
        
        response = self.model.generate_content(prompt, generation_config=generation_config)
        return self._process_content(response.text, is_json)

    def _parse_blackbox_response(self, raw_text):
        if "data: " in raw_text:
            for line in raw_text.split("\n"):
                if line.startswith("data: ") and "choices" in line:
                    try:
                        return json.loads(line[6:])['choices'][0]['message']['content']
                    except: continue
        try:
            return json.loads(raw_text)['choices'][0]['message']['content']
        except:
            return raw_text

    def _process_content(self, content, is_json):
        if not is_json: return content
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try: return json.loads(json_match.group(0))
            except: pass
        try: return json.loads(content)
        except: return {"explanation": content, "remediation_steps": [], "code_example": ""}

    def _build_remediation_prompt(self, vuln_type, severity, url, parameter, payload, evidence):
        vuln_label = 'SQL Injection' if vuln_type == 'sqli' else 'XSS'
        return f"""Analyze this {vuln_label} finding and respond with JSON only:
URL: {url}
Parameter: {parameter}
Payload: {payload}

JSON format:
{{
  "explanation": "Brief explanation",
  "remediation_steps": ["Step 1", "Step 2"],
  "code_example": "Code snippet"
}}"""
