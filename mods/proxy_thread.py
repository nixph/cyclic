import socket
from threading import Thread
from mods.raw_http_parser import RawHTTPParser
from mods.pyfunc import receive_from, close_socket_pass_exc

class ProxyThread(Thread):
    def __init__(self, client_socket, client_address, server_socket=None):
        Thread.__init__(self, daemon=True)
        self.server_socket = server_socket
        self.client_socket = client_socket
        self.client_address = client_address
    def connect_relay(self, request):
        pass
    def run(self):
        data = receive_from(self.client_socket)
        #print(' Data:',data)
        request = RawHTTPParser(data)
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
