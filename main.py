import os, json, requests
import uvicorn
import socket, time, re
from mods.proxy import Proxy
from threading import Thread
from mods.pyfunc import parse_headers, parse_query, headers_to_list, read_body, get_socket_from_free_port, wait_for_sleep

class CliHandler(Thread):
    def __init__(self, cli_socket, cli_address, server_socket):
        Thread.__init__(self, daemon=True)
        self.cli_socket = cli_socket
        self.cli_address = cli_address
        self.server_socket = server_socket
    def run(self):
        print(' [=] Incoming connection from %s:%d' % self.cli_address)
class MainHandler(Thread):
    def __init__(self, addr='127.0.0.1', port=3000):
        Thread.__init__(self, daemon=True)
        self.addr = addr
        self.port = port

    def run(self):
        _socket = get_socket_from_free_port(addr=self.addr,port=self.port)
        _socket_addr = _socket.getsockname()
        print(" [*] Started listening on {}:{}".format(_socket_addr[0],_socket_addr[1]))
        _socket.listen(5)
        while True:
            try:
                cli_socket, cli_address = _socket.accept()
                #print(' [=] Incoming connection from %s:%d' % cli_address)
                cli_thread = CliHandler(cli_socket, cli_address, _socket)
                cli_thread.start()
            except Exception as e:
                print(" Error Proxy:",e)



if __name__ == "__main__":
    MainHandler(port=3000).start()
    wait_for_sleep()
    #uvicorn.run("main:app", host="0.0.0.0", port=3000, log_level="critical")
    #config = uvicorn.Config("main:app", port=5000, log_level="info")
    #server = uvicorn.Server(config)
    #server.run()






























#
