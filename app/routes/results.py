"""
Results routes - Display scan results
"""

from flask import Blueprint, render_template

results_bp = Blueprint('results', __name__)


@results_bp.route('/<int:scan_id>')
def show_results(scan_id):
    """Display results for a specific scan session."""
    # TODO: Replace mock data with actual database queries in Phase 3
    scan = {
        'id': scan_id,
        'target': 'target-website.com',
        'pages_crawled': 24,
        'forms_found': 8,
        'vuln_count': 5,
    }

    ai_summary = {
        'model': 'RandomForest',
        'accuracy': '94.2%',
        'suspicious': '3 / 8 responses',
    }

    vulnerabilities = [
        {
            'type_class': 'sqli',
            'type_label': 'SQL Injection',
            'severity': 'HIGH',
            'severity_class': 'high',
            'url': '/login.php',
            'payload': "' OR '1'='1",
            'evidence': 'SQL syntax error in response body',
            'ai_label': 'Suspicious',
            'ai_confidence': 88.5,
        },
        {
            'type_class': 'xss',
            'type_label': 'XSS',
            'severity': 'MEDIUM',
            'severity_class': 'medium',
            'url': '/search?q=',
            'payload': '<script>alert(1)</script>',
            'evidence': 'Payload reflected in response',
            'ai_label': 'Suspicious',
            'ai_confidence': 76.2,
        },
    ]

    return render_template(
        'results.html',
        scan=scan,
        ai_summary=ai_summary,
        vulnerabilities=vulnerabilities,
    )
