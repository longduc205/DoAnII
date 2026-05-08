from app.services.detector import VulnerabilityDetector
import logging
logging.basicConfig(level=logging.INFO)

detector = VulnerabilityDetector()
# Add the cookies manually for the test
detector.session.cookies.set('PHPSESSID', 'g4lf3381t4oikauihrv5k69t70')
detector.session.cookies.set('security', 'low')

form_data = {
    'action': 'http://dvwa:80/vulnerabilities/sqli/',
    'method': 'GET',
    'page_url': 'http://dvwa:80/vulnerabilities/sqli/',
    'inputs': [
        {'name': 'id', 'type': 'text', 'value': ''},
        {'name': 'Submit', 'type': 'submit', 'value': 'Submit'},
        {'name': 'user_token', 'type': 'hidden', 'value': 'dummy_token'}
    ]
}

findings = detector.test_sqli(form_data)
print("Findings:")
for f in findings:
    print(f)
