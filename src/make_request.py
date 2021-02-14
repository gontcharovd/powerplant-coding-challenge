import requests

url = 'http://127.0.0.1:8000/productionplan/'
payload = open('example_payloads/payload1.json', 'rb').read()
response = requests.post(url, data=payload)

print(response.json())
