import os, json, requests
import uvicorn

import socket, time, re
from threading import Thread
from typing import Optional
class RawHTTPParser:
    def __init__(self, raw: bytes):
        #print(raw)
        self.ok = True
        self.raw = raw
        self.uri = None
        self.host = None
        self.port = None
        self.body = b''
        self.method = None
        self.headers = {}
        self.protocol_version = None
        try:
            raw, self.body = raw.split(b"\r\n\r\n")
        except Exception as e:
            pass
        raw = raw.split(b"\r\n")
        #print(raw)
        try:
            self.method, self.uri, self.protocol_version = [x.decode() for x in raw[0].split(b" ")]
        except Exception as e:
            self.ok = False
            pass#print(" Error:",e)
        #print(self.method, self.uri, self.protocol_version)
        try:
            self.port = int(self.uri.split(":")[1].split("/")[0])
        except Exception as e:
            pass#print(" Error:",e)
        #print(self.port)
        try:
            self.host = raw[1].split(b'Host: ')[1].decode()
            #print(_host)
        except Exception as e:
            pass#print(" Error:",e)

        try:
            for i in range(2,len(raw)):
                key_value = raw[i].split(b':')
                if len(key_value) == 2:
                    self.headers.update({key_value[0].lower().decode():key_value[1].strip().decode()})
                #print(i)
        except Exception as e:
            pass#print(" Error:",e)


        #if not self.method or not self.host:
        #    self.is_parse_error = True


    def get_port(self, uri):
        pass


    @staticmethod
    def to_str(item: Optional[bytes]) -> Optional[str]:
        if item:
            return item.decode('charmap')

    @staticmethod
    def to_int(item: Optional[bytes]) -> Optional[int]:
        if item:
            return int(item)

    def __str__(self):
        return str(dict(URI=self.uri, HOST=self.host, PORT=self.port, METHOD=self.method))

def get_socket_from_free_port(addr='127.0.0.1', port=None):
    _fromport = port if port else 4000
    _toport = port+1 if port else 9000
    for port in range(_fromport, _toport):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((addr, port))
            return sock
        except Exception as e:
            print(" Error:",e)
            continue
    raise ValueError(" Error Getting Socket")
def close_socket_pass_exc(conn: socket.socket):
    try:
        conn.close()
    except Exception as e:
        print(" Error:",e)
def receive_from(conn: socket.socket, chunk_size=2048, timeout=.1):
    buffer = b''
    conn.settimeout(timeout)
    try:
        while 1:
            data = conn.recv(chunk_size)
            if not data:
                break
            buffer += data
    except Exception as e:
        #print(" Error Receive:",e)
        if len(e.args) >= 2 and e.args[1] == 'Transport endpoint is not connected':
            return False
    return buffer
class ProxyThread(Thread):
    def __init__(self, client_socket, client_address, server_socket=None):
        Thread.__init__(self, daemon=True)
        self.server_socket = server_socket
        self.client_socket = client_socket
        self.client_address = client_address
    def connect_relay(self, request):
        pass
    def run(self):
        #data = receive_from(self.client_socket)
        #request = RawHTTPParser(data)
        request = RawHTTPParser(b'CONNECT example.com:443 HTTP/1.0\r\n\r\n')
        if request.ok:
            print(request.raw)
            _addr = request.uri.split(':')[0]
            _port = request.port if request.port else 443
            try:
                _sock = socket.create_connection((_addr,_port), timeout=5)
                print(" {} connected.".format(_addr))
            except Exception as e:
                print(" Error:",e)
                return
            print(" Sending Client Negotiation.")
            self.client_socket.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
            fail_count = 0
            while True:
                local_buffer = receive_from(self.client_socket)
                print(" Local Buffer:",local_buffer)
                if len(local_buffer):
                    _sock.sendall(local_buffer)
                remote_buffer = receive_from(_sock)
                print(" Remote Buffer:",remote_buffer)
                if len(remote_buffer):
                    self.client_socket.sendall(remote_buffer)
                fail_count = fail_count+1 if (not len(local_buffer) and not len(remote_buffer)) else 0
                if fail_count >= 3: break
            close_socket_pass_exc(self.client_socket)
            close_socket_pass_exc(_sock)
            print(' DONE!')
class Proxy(Thread):
    def __init__(self, addr='0.0.0.0', port=None):
        Thread.__init__(self, daemon=True)
        self.addr = addr
        self.port = port
        self.start()
    def run(self):
        _socket = get_socket_from_free_port(port=self.port)
        _socket.listen(5)
        while True:
            try:
                client_socket, client_address = _socket.accept()
                print(' [=] Incoming connection from %s:%d' % client_address)
                proxy_thread = ProxyThread(client_socket, client_address, _socket)
                proxy_thread.start()
            except Exception as e:
                print(" Error Proxy:",e)

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
        #print(" Message:",message)
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
    #print(" Path:",scope['path'])
    if scope['path'] == '/':
        _sock = get_socket_from_free_port()
        _sock.connect(('127.0.0.1',8080))

        data = _sock.recv(1024)
        print(" Client Receive:",data)
        _sock.sendall(b'sampledata')

        print(" rootweb")
    elif scope['path'] == '/webhook':
        print(" webhook")
        if scope['method'] == 'GET':
            pass
        elif scope['method'] == 'POST':
            pass
    #else:





    body = b'Hello World!'
    await response(send, headers={}, status_code=200)
    await response(send, body=body)

if __name__ == "__main__":
    proxy = Proxy(port=8080)


    uvicorn.run("debug:app", host="0.0.0.0", port=8181)
    #config = uvicorn.Config("main:app", port=5000, log_level="info")
    #server = uvicorn.Server(config)
    #server.run()
