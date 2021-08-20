import socket
import utils


class Client:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.room = None
        self.connected = True

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((utils.MAIN_HOST, utils.MAIN_PORT))

    def set_room(self, room):
        self.room = room

    def send_message(self, message):
        self.sock.send(message.encode('utf-8'))

    def is_host(self):
        return self.room.host.id == self.id

    def disconnect(self):
        self.connected = False
        self.room.delete_user(self)
        self.sock.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

client_name = input("Whats' tou your name?")
sock.send(client_name.encode('utf-8'))
print(sock.recv(1024).decode('utf-8'))
