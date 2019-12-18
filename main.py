import socket
import os.path as os
import threading

CONTENT_TYPE_DICT = {'html': b'Content-Type: text/html\n',
                     'jpeg': b'Content-Type: image/jpeg\n',
                     'png': b'Content-Type: image/png\n',
                     'ico': b'Content-Type: image/x-icon\n',
                     None: b''}


class ParseException(BaseException):
    def __str__(self):
        return "ERROR PARSING REQUEST"


class FileTypeException(BaseException):
    def __str__(self):
        return "ERROR FILE TYPE NOT SUPPORTED"


class ClientThread(threading.Thread):
    def __init__(self, thread_socket, thread_address):
        print(thread_socket, thread_address)
        threading.Thread.__init__(self)
        self.socket = thread_socket
        self.address = thread_address

    def run(self):
        try:
            self.handle()
        except ParseException as e:
            print(e)
        except FileTypeException as e:
            print(e)
        finally:
            self.socket.close()

    def handle(self):
        r = Request(self.socket.recv(2048).decode())
        r.url = r.url[1::]
        self.response(r)

    @staticmethod
    def gen_header(request):
        headers = b'Connection: Keep-Alive\n'
        with open(request.url, 'rb+') as file:
            headers += b"Content-Length:" + str(len(file.read())).encode() + b'\n'
            if request.file_type not in CONTENT_TYPE_DICT:
                print(CONTENT_TYPE_DICT.keys())
                raise FileTypeException
            headers += CONTENT_TYPE_DICT[request.file_type]
        return headers

    def response(self, request):
        if os.exists(request.url):
            with open(request.url, 'rb+') as file:
                r = Response(data=file.read(), status='200 OK', headers=self.gen_header(request)).__bytes__()
        else:
            r = Response(data=b'404 FILE NOT FOUND', status='404 Not Found', headers=b"Server: <3\n").__bytes__()
        print('->', r)
        self.socket.sendall(r)
        self.socket.close()


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
        self.method, self.url, self.headers, self.file_type = self.parse(raw)

    @staticmethod
    def parse(raw):
        raw = raw.split('\n')
        print(raw)
        request = raw[0].split(' ')
        print(request)
        method, url = request[0], request[1]
        headers = raw[1:-1]
        if '.' not in url and url is not r'/' and url is not '.':
            raise ParseException()
        if url == '/':
            url = '/index.html'
        file_type = url.split('.')[-1]
        return method, url, headers, file_type


class Server:
    def __init__(self, ip='localhost', port=8080):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = ip, port
        self.start()

    def start(self):
        self.socket.bind((self.ip, self.port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[+] Listening for connections on port %d" % self.port)
        while True:
            self.socket.listen(1)
            thread = ClientThread(*self.socket.accept())
            thread.start()


def main():
    server = Server()
    server.start()


if __name__ == '__main__':
    main()

