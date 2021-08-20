import socket
import functools
import threading
import time

import client_server as cl
import utils
from room import Room

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

DEBUG = True


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print('Calling {} with {}'.format(func.__name__, args))
        return func(*args, **kwargs)

    if DEBUG:
        return wrapper

    return func


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

        self.admin = cl.ClientServer(-1, 'ADMIN', None)
        self.hub = Room(-1, self.admin, 'HUB')

    def run(self):
        while True:
            sock, addr = self.server.accept()
            name = sock.recv(utils.SIZE).decode(utils.ENCODING)

            user = self.create_user(name, sock)
            self.send_room_list(user)

            thread = threading.Thread(target=self.handle_user, args=(user, sock, addr))
            thread.start()

    def handle_user(self, user, sock, addr):
        while user.connected:
            message = sock.recv(utils.SIZE).decode(utils.ENCODING).strip()
            print('[{}]: {}'.format(user.name, message))
            if message.startswith('!'):
                params = message.split()
                self.process_command(params, user)
            else:
                for other_user_id, other_user in self.connected_users.items():
                    if other_user_id != user.id and other_user.room == user.room:
                        self.send_message(user.name, other_user, message)

    @log
    def process_command(self, params, user):
        command = params[0]
        if command == '!list':
            self.send_room_list(user)
        elif command == '!exit':
            user.disconnect()
        elif command == '!connect':
            pass
        elif command == '!create':
            name = params[1]
            self.create_room(user, name)
        elif command == '!kick' and user.is_host():
            username = params[1]
            user.room.delete_user(username)

    @log
    def create_user(self, name, sock):
        id = self.USER_ID

        user = cl.ClientServer(id, name, sock)
        user.set_room(self.hub)

        self.connected_users[id] = user
        self.USER_ID += 1

        return user

    @log
    def create_room(self, user, name, password=None):
        id = self.ROOM_ID

        room = Room(id, user, name, password)
        room.add_user(user)

        self.rooms[id] = room
        self.ROOM_ID += 1

        return room

    def connect_user_to_room(self, user):
        pass

    def disconnect_user(self, user):
        pass

    def kick_user(self, user):
        pass

    @log
    def send_room_list(self, user):
        for room in self.rooms.values():
            self.send_message('SERVER', user, room.name)

    @log
    def send_message(self, sender_name, user, message):
        sock = user.sock
        message_to_send = '\n[{}]: {}\n'.format(sender_name, message)
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
