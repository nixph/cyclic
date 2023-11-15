import socket, time



def get_receivers():
    





















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
def receive_from(conn: socket.socket, chunk_size=2048, timeout=.01):
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

def parse_headers(_headers) -> dict:
    return {x[0].decode().lower():x[1].decode() for x in _headers if len(x) == 2}

def parse_query(_query) -> dict:
    if isinstance(_query, bytes): _query = _query.decode('utf-8')
    query_split = _query.split("&")
    return {x.split("=")[0]:x.split("=")[1] for x in query_split if len(x.split("=")) == 2}


async def read_body(_receiver):
    body = b''
    more_body = True
    while more_body:
        message = await _receiver()
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


def wait_for_sleep():
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        pass

























#
