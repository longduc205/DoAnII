"""
AI Chat routes — Q&A endpoint for vulnerability findings.

Provides a POST endpoint that accepts a user question
(optionally with vulnerability context) and returns an
AI-generated answer via the Gemini-backed AIAdvisor.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required

from app.models.vulnerability import Vulnerability
from app.services.ai_advisor import AIAdvisor

ai_chat_bp = Blueprint('ai_chat', __name__)


@ai_chat_bp.route('/ask', methods=['POST'])
@login_required
def ask_ai():
    """Answer a user question about a vulnerability finding.

    Request JSON:
        {
            "question": "How do I fix this?",
            "vulnerability_id": 42   (optional)
        }

    Response JSON:
        { "answer": "..." }
    """
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    vuln_id = data.get('vulnerability_id')

    if not question:
        return jsonify({'error': 'Question is required.'}), 400

    # Build finding context if a vulnerability ID was supplied
    finding_context = None
    if vuln_id:
        vuln = Vulnerability.query.get(vuln_id)
        if vuln:
            finding_context = {
                'vuln_type': vuln.vuln_type,
                'severity': vuln.severity,
                'url': vuln.url,
                'parameter': vuln.parameter,
                'payload': vuln.payload,
                'evidence': vuln.evidence,
            }

    api_key = current_app.config.get('GEMINI_API_KEY', '')
    advisor = AIAdvisor(api_key=api_key)
    answer = advisor.ask_question(question, finding_context)

    return jsonify({'answer': answer})
