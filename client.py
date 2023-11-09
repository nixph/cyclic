import requests
url = 'http://localhost:8181/webhook'

data = {
    'key':'value'
}
response = requests.post(url, json=data)
print(response.content)
