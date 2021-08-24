import sys
import threading

from server.server import Server
from client.client import Client


def sending(user):
    working = True
    while working:
        try:
            message = input('[{}]: '.format(user.name))
            user.send_message(message)
            if message == '!exit':
                sys.exit()
        except Exception as e:
            print("[ERROR] can't send message to server")
            working = False


def receiving(user):
    working = True
    while working:
        try:
            message = user.get_message()
            if message:
                print(message)
        except Exception as e:
            print("[ERROR] can't receive message from server")
            working = False


def test():
    command = input('Run server on your computer? [Y/N] ')
    if command.lower() == 'y':
        chat_server = Server()
        chat_server.run()
    else:
        username = input('Enter you name: ')
        user = Client(username)
        user.connect()

        sending_thread = threading.Thread(target=sending, args=(user,))
        receiving_thread = threading.Thread(target=receiving, args=(user,))

        sending_thread.start()
        receiving_thread.start()


if __name__ == '__main__':
    test()
