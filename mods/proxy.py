
from threading import Thread
from mods.pyfunc import get_socket_from_free_port
from mods.proxy_thread import ProxyThread

class Proxy(Thread):
    def __init__(self, addr='127.0.0.1', port=None):
        Thread.__init__(self, daemon=True)
        self.addr = addr
        self.port = port
        self.start()
    def run(self):
        _socket = get_socket_from_free_port(addr=self.addr,port=self.port)
        _socket_addr = _socket.getsockname()
        print(" [*] Started listening on {}:{}".format(_socket_addr[0],_socket_addr[1]))
        _socket.listen(5)
        while True:
            try:
                client_socket, client_address = _socket.accept()
                print(' [=] Incoming connection from %s:%d' % client_address)
                proxy_thread = ProxyThread(client_socket, client_address, _socket)
                proxy_thread.start()
            except Exception as e:
                print(" Error Proxy:",e)
