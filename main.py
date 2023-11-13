import os, json, requests
import uvicorn
import socket, time, re
from mods.proxy import Proxy
from threading import Thread
from mods.pyfunc import parse_headers, parse_query, headers_to_list, receive_from, get_socket_from_free_port, wait_for_sleep

class CliHandler(Thread):
    def __init__(self, cli_socket, cli_address, server_socket):
        Thread.__init__(self, daemon=True)
        self.cli_socket = cli_socket
        self.cli_address = cli_address
        self.server_socket = server_socket
    def run(self):

        print(' [=] Incoming connection from %s:%d' % self.cli_address)
        try:
            _sock = socket.create_connection(("example.com",443), timeout=5)
            print(" {} connected.".format("example.com"))
        except Exception as e:
            print(" Error Creating Connection:",e)
        #return b"Hello World"
        self.cli_socket.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
        self.cli_socket.sendall(b"Hello World")
        #data = receive_from(self.cli_socket)
        #print(" [*] Incoming Data:",data)
data_hold = []

async def read_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

async def app(scope, receive, send):
    #assert scope['type'] == 'http'
    global data_hold
    data_hold.append('client'+str(len(data_hold)))

    body = await read_body(receive)
    print(data_hold)




    await send({'type': 'http.response.start','status': 200,'headers': [[b'content-type', b'text/plain'],],})
    await send({'type': 'http.response.body','body': b'Hello, World!',})


if __name__ == "__main__":
    #main()
    #MainHandler(port=3000).start()
    #wait_for_sleep()
    uvicorn.run("main:app", host="0.0.0.0", port=3000, log_level="critical")
    #config = uvicorn.Config("main:app", port=5000, log_level="info")
    #server = uvicorn.Server(config)
    #server.run()






























#
