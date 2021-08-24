import utils
import socket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
ENCODING = 'utf-8'


class Client:

    def __init__(self, name):
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

    def connect(self):
        self.sock.send(self.name.encode(ENCODING))

    def send_message(self, message):
        self.sock.send(message.encode(ENCODING))

    def get_message(self):
        return self.sock.recv(utils.SIZE).decode(ENCODING)
