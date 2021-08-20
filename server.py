import socket
import functools
import threading

import client as cl
import utils
from room import Room

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050


def singleton(cls):
    instance = None

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        nonlocal instance
        if not instance:
            instance = cls(*args, **kwargs)
        return instance

    return wrapper


class IdField:

    def __init__(self):
        self.value = 0

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        value = getattr(instance, self.name)

        return value

    def __set__(self, instance, value):
        setattr(instance, self.name, value)


@singleton
class Server:
    USER_ID = 0
    ROOM_ID = 0

    def __init__(self):
        self.rooms = {}
        self.connected_users = {}

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()

    def run(self):
        while True:
            sock, addr = self.server.accept()
            name = ''
            self.create_user(sock, name)
            thread = threading.Thread(target=self.handle_user, args=(sock, addr))
            thread.start()

    def handle_user(self, user, sock, addr):
        while user.connected:
            message = sock.recv(utils.SIZE).decode(utils.ENCODING).strip()
            if message.startswith('!'):
                self.process_command(message[1:], user)
            else:
                for user_id, user_ins, user_socket in self.connected_users.items():
                    if user_id != user.id and user_ins.room == user.room:
                        self.send_message(user, message)

    def process_command(self, command, user):
        if command == 'list':
            self.send_room_list(user)
        elif command == 'exit':
            user.disconnect()
        elif command == 'connect':
            pass
        elif command == 'create':
            name, *password = command.split()[1:]
            self.create_room(user, name, password)
        elif command == 'kick' and user.is_host():
            command, *username = command.split()
            user.room.delete_user(*username)

    def create_user(self, sock, name):
        id = self.USER_ID
        user = cl.Client(id, name)
        self.connected_users[id] = user

    def create_room(self, user, name, password):
        id = self.ROOM_ID
        room = Room(id, name, password)
        room.add_user(user)
        self.rooms[id] = room
        self.ROOM_ID += 1

    def disconnect_user(self, user):
        pass

    def kick_user(self, user):
        pass

    def send_room_list(self, user):
        for room in self.rooms.values():
            self.send_message(user, room.name)

    def send_message(self, user, message):
        sock = user.sock
        message_to_send = '[{}]: {}'.format(user.name, message)
        sock.send(message_to_send.encode(utils.ENCODING))

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind((HOST, PORT))
# server.listen()
#
# while True:
#     sock, addr = server.accept()
#     print('[CONNECTION] Connected to {}!'.format(addr))
#
#     message = sock.recv(1024).decode('utf-8')
#     print('[EVENT] Message from {} is {}.'.format(addr, message))
#
#     sock.send('[SERVER] Got you message, {}!'.format(addr).encode('utf-8'))
#     sock.close()
