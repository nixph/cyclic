import requests

poster_url = "https://image.tmdb.org/t/p/w600_and_h600_bestv2/cMD9Ygz11zjJzAovURpO75Qg7rT.jpg"
url = "http://localhost:8080/dcproxy?url="+poster_url

headers = {'Authorization':'sample_token'}
response = requests.get(url,headers=headers, timeout=10)

print(response.status_code)
print(response.content)
