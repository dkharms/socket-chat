import utils
import socket
import functools
import threading

from .client_server import ClientServer
from .room import Room

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

LOGGING = True


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print('Calling {} with {}'.format(func.__name__, args))
        return func(*args, **kwargs)

    if LOGGING:
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

        self.admin = ClientServer(-1, 'ADMIN', None, None)
        self.hub = self.create_room(self.admin, 'HUB')

    def run(self):
        while True:
            sock, address = self.server.accept()
            name = sock.recv(utils.SIZE).decode(utils.ENCODING)
            user = self.create_user(name, sock, address)
            thread = threading.Thread(
                target=self.handle_user, args=(user, sock, address))
            thread.start()

    def handle_user(self, user: ClientServer, sock, address):
        running = True
        while running:
            try:
                message = sock.recv(utils.SIZE).decode(utils.ENCODING).strip()
                print('[{}]: {}'.format(user.name, message))
                if message.startswith('!'):
                    params = message.split()
                    self.process_command(params, user)
                else:
                    for other_user_id, other_user in self.connected_users.items():
                        if other_user_id != user.client_id and other_user.room == user.room:
                            self.send_message(user.name, other_user, message)
            except Exception as e:
                message = '[SERVER]: connection with {} is terminated'.format(user)
                print(message)
                running = False

    @log
    def process_command(self, params, user: ClientServer):
        command = params[0]
        if command == '!list':
            self.send_room_list(user)
        elif command == '!create':
            name = params[1]
            password = None
            if len(params) == 3:
                password = params[2]
            self.create_room(user, name, password)
        elif command == '!connect':
            room_name = params[1]
            self.connect_user_to_room(user, room_name)
        elif command == '!kick' and user.is_host():
            username = params[1]
            self.kick_user(username, user)
        elif command == '!hub':
            self.connect_user_to_room(user, 'HUB')
        elif command == '!exit':
            message = 'user [{}] left room'.format(user.name)
            self.disconnect_user(user, message)

    @log
    def create_user(self, name: str, sock, address):
        user_id = self.USER_ID
        user = ClientServer(user_id, name, sock, address)
        self.hub.add_user(user)
        self.connected_users[user_id] = user
        self.USER_ID += 1

        return user

    @log
    def create_room(self, user: ClientServer, name: str, password=None):
        room_id = self.ROOM_ID
        chat_room = Room(room_id, user, name, password)
        chat_room.add_user(user)
        self.rooms[room_id] = chat_room
        self.ROOM_ID += 1

        return chat_room

    @log
    def connect_user_to_room(self, user: ClientServer, room_name: str):
        chat_room = self.find_room_by_name(room_name)
        if chat_room:
            password = None
            if chat_room.password:
                message = 'enter password for [{}] room'.format(room_name)
                self.send_message('SERVER', user, message)
                password = user.sock.recv(utils.SIZE).decode(utils.ENCODING).strip()
            if password == chat_room.password:
                current_room = user.room
                current_room.delete_user(user.client_id)
                chat_room.add_user(user)
        else:
            message = 'room with [{}] name not found'.format(room_name)
            self.send_message('SERVER', user, message)

    @log
    def disconnect_user(self, user: ClientServer, message: str):
        for other_user_id, other_user in self.connected_users.items():
            if other_user_id != user.client_id and other_user.room == user.room:
                self.send_message('SERVER', other_user, message)

        user.disconnect()
        del self.connected_users[user.client_id]

    @log
    def kick_user(self, username: str, host: ClientServer):
        user_to_kick = self.find_user_by_name(username)
        if user_to_kick:
            message = 'user [{}] was kicked by [{}]'.format(
                username, host.name)
            self.disconnect_user(user_to_kick, message)
        else:
            message = 'user with name [{}] not found'.format(username)
            self.send_message('SERVER', host, message)

    @log
    def send_room_list(self, user: ClientServer):
        for chat_room in self.rooms.values():
            self.send_message('SERVER', user, chat_room.name)

    @log
    def send_message(self, sender_name: str, user: ClientServer, message: str):
        sock = user.sock
        message_to_send = '[{}]: {}'.format(sender_name, message)
        sock.send(message_to_send.encode(utils.ENCODING))

    @log
    def find_user_by_name(self, username: str):
        for user in self.connected_users.values():
            if user.name == username:
                return user

        return None

    @log
    def find_room_by_name(self, room_name: str):
        for chat_room in self.rooms.values():
            if chat_room.name == room_name:
                return chat_room

        return None

    def __repr__(self):
        return 'SERVER | SOCKET: {}'.format((HOST, PORT))
