import socket
import os.path as os
import threading


class ClientThread(threading.Thread):
    def __init__(self, accepted):
        threading.Thread.__init__(self)
        self.socket = accepted[0]
        self.address = accepted[1]
        print("New connection added: ", self.address)

    def run(self):
        print("Connection from : ", self.address)
        while True:
            self.handle()
        #print("Client at ", self.address, " disconnected...")

    def handle(self):
        r = Request(self.socket.recv(4096).decode())
        if r.url == '/':
            r.url = '/index.html'
        r.url = r.url[1::]
        self.response(r)

    def response(self, request):
        print('\n[*] New Request :', request.url)
        if os.exists(request.url):
            with open(request.url, 'rb+') as file:
                r = Response(data=file.read(), status='200 OK', headers=b'Connection: Keep-Alive\nServer: LAXCITY\n').__bytes__()
        else:
            r = Response(data=b'404 FILE NOT FOUND', status='404 Not Found', headers=b"Server: LAXCITY\n").__bytes__()
        print('->', r)
        self.socket.sendall(r)


class Response:
    def __init__(self, data, headers, status):
        self.data = data
        self.headers = headers
        self.status = status.encode()

    def __bytes__(self):
        return b'HTTP/1.1 ' + self.status + b'\n' + self.headers + b'\n' + self.data


class Request:
    def __init__(self, raw):
        self.raw = raw
        self.method, self.url, self.headers = self.parse(raw)

    def parse(self, raw):
        raw = raw.split('\n')
        print(raw)
        request = raw[0].split(' ')
        print(request)
        method, url = request[0], request[1]
        headers = raw[1:-1]
        return method, url, headers


class Server:
    def __init__(self, ip='localhost', port=80):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = ip, port
        #self.client = (None, None)
        self.start()

    def start(self):
        self.socket.bind((self.ip, self.port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.socket.settimeout(100)
        #self.socket.listen(10)
        print("[+] Listening for connections on port %d" % self.port)
        while True:
            self.socket.listen(1)
            thread = ClientThread(self.socket.accept())
            thread.start()
            #self.client = self.socket.accept()
            #self.handle()
    """
    def handle(self):
        r = Request(self.client[0].recv(2048).decode())
        if r.url == '/':
            r.url = '/index.html'
        r.url = r.url[1::]
        self.response(r)

    def response(self, request):
        print('\n[*] New Request :', request.url)
        if os.exists(request.url):
            with open(request.url, 'rb+') as file:
                r = Response(data=file.read(), status='200 OK', headers=b'Connection: Keep-Alive\nServer: LAXCITY\n').__bytes__()
        else:
            r = Response(data=b'404 FILE NOT FOUND', status='404 Not Found', headers=b"Server: LAXCITY\n").__bytes__()
        print('->', r)
        self.client[0].sendall(r)
    """

def main():
    server = Server()
    server.start()


if __name__ == '__main__':
    main()
