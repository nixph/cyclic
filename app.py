import requests
from flask import Flask, request
import os
class DummyResponse(object):
    def __init__(self):
        super(DummyResponse, self).__init__()
        self.ok = False
        self.content = b''
        self.status_code = 400
app = Flask(__name__)
session = requests.Session()
@app.route('/dcproxy')
def dc_proxy():
    if request.headers.get('Authorization') and request.args.get('url'):
        headers = {"Authorization": request.headers['Authorization'], "Content-Type": "application/json",'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        try:
            response = session.post('https://discord.com/api/v9/unfurler/unfurl',json={'url':request.args['url']},headers=headers)
        except Exception as e:
            print(" error:",e)
            response = DummyResponse()
        if response.ok:
            return "mp:"+"/".join("://".join(response.json()['embeds'][0]['thumbnail']['proxy_url'].split("://")[1:]).split("/")[1:])
    return 'dc proxy!', 401

@app.route('/')
def hello_world():
    return 'Hello, world!'


































#
