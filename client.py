import requests
url = 'https://example.com'

data = {
    'key':'value'
}
proxies = {
    'http':'http://localhost:8080',
    'https':'http://localhost:8080'
}
response = requests.post(url, json=data, proxies=proxies)
print(response.content)
