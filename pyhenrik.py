import requests

def get_account(_url):
    if _url:
        try:
            return requests.get(_url, headers={'accept': 'application/json'}, timeout=10).json()['data']
        except Exception as e:
            print(" Error:",e)
    return {}

def get_last_match_ts(_puuid, _region='ap', _size=1):
    url = 'https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/{}/{}?size={}'.format(_region, _puuid, _size)
    try:
        response = requests.get(url, headers={'accept': 'application/json'}, timeout=10).json()['data'][0]
        return response['metadata']['game_start']+response['metadata']['game_length']
    except Exception as e:
        print(" Error:",e)
    return {}
