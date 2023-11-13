import os, json, requests
import uvicorn
from pygithub import GithubClient
from pymessenger import MessengerClient
from dotenv import load_dotenv
load_dotenv()

#os.system('cls')
github = GithubClient(os.getenv('GITHUB_USER'),os.getenv('GITHUB_REPO'),os.getenv('GITHUB_TOKEN'),os.getenv('GITHUB_VERSION'),os.getenv('GITHUB_BASE_URL'))
messenger = MessengerClient(os.getenv('MESSENGER_TOKEN'),os.getenv('MESSENGER_PAGE_ID'),os.getenv('MESSENGER_GRAPH_VERSION'))

#target_list = []
target_list = github.get_targets()
recipient_list = github.get_recipients()

def parse_headers(_headers) -> dict:
    return {x[0].decode().lower():x[1].decode() for x in _headers if len(x) == 2}

def parse_query(query_str) -> dict:
    if isinstance(query_str, bytes): query_str = query_str.decode('utf-8')
    query_split = query_str.split("&")
    return {x.split("=")[0]:x.split("=")[1] for x in query_split if len(x.split("=")) == 2}

async def read_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        print(" Message:",message)
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

async def headers_to_list(_headers):
    _response = []
    for key in _headers:
        key_hold = key
        value_hold = _headers[key]
        if isinstance(key_hold, str): key_hold = key_hold.encode()
        if isinstance(value_hold, str): value_hold = value_hold.encode()
        _response.append((key_hold,value_hold))
    return _response

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
    if scope['path'] == '/':
        _sock = get_socket_from_free_port()
        _sock.connect(('127.0.0.1',8080))

        data = _sock.recv(1024)
        print(" Client Receive:",data)
        _sock.sendall(b'sampledata')

        print("rootweb")
    elif scope['path'] == '/webhook':
        if scope['method'] == 'GET':
            query = parse_query(scope['query_string'])
            if query.get('hub.mode') == 'subscribe' and query.get('hub.challenge'):
                return await response(send, body=query['hub.challenge'], headers={}, status_code=200)
        elif scope['method'] == 'POST':
            if headers.get('content-type') == 'application/json':
                data = json.loads(body)
                sender_id = data['entry'][0]['messaging'][0]['sender']['id']
                sender_text = data['entry'][0]['messaging'][0]['message']['text']

                print(sender_id,sender_text)

                #resp = messenger.send_message(sender_id,sender_text)
                #print(resp)

        #print(" Scope:",scope)
        #print(' Body:',body)



    body = b'Hello World!'
    await response(send, headers={}, status_code=200)
    await response(send, body=body)

if __name__ == "__main__":
    uvicorn.run("backup:app", port=5000, log_level="info")
    #config = uvicorn.Config("main:app", port=5000, log_level="info")
    #server = uvicorn.Server(config)
    #server.run()
