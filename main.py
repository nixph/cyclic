import os, json, requests
import uvicorn
import socket, time, re
from mods.proxy import Proxy
#from threading import Thread
from mods.pyfunc import parse_headers, parse_query, headers_to_list, read_body



async def response(send, body=None, headers={}, status_code=None):
    if status_code:
        headers = await headers_to_list(headers)
        await send({'type': 'http.response.start','status': 200,'headers': headers})
    if body:
        if isinstance(body, str): body = body.encode()
        await send({'type': 'http.response.body','body': body,})

async def app(scope, receive, send):
    body = await read_body(receive)
    headers = parse_headers(scope['headers'])
    #print(' SCOPE:',scope)
    if scope['path'] == '/':
        print(" webroot")
    elif scope['path'] == '/webhook':
        print(" webhook")
    elif scope['path'] == '/client':
        print(" client")
        proxies = {'http':'http://localhost:8080','https':'http://localhost:8080'}
        try:
            #response = requests.get('https://example.com', proxies=proxies, timeout=10)
            print(' Response:',response.content)
        except Exception as e:
            pass
            #print(" Error:",e)





    await send({'type': 'http.response.start','status': 200,'headers': await headers_to_list(headers)})
    await send({'type': 'http.response.body','body': body,})
    #await response(send, body=body)

if __name__ == "__main__":
    proxy = Proxy(port=8080)
    uvicorn.run("main:app", host="0.0.0.0", port=3000, log_level="critical")
    #config = uvicorn.Config("main:app", port=5000, log_level="info")
    #server = uvicorn.Server(config)
    #server.run()






























#
