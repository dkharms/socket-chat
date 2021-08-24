import threading
import sys
import client as cl
import server as sv


# def mainloop(user):
#     message = input('[MESSAGE]: ')
#     if message.startswith('!'):
#         process_command(message[1:], user)
#     else:
#         user.send_message(message)
#
#
# def main():
#     global server
#     command = input('Run server on your computer? [Y/N] ')
#     if command.lower() == 'y':
#         server = sv.Server()
#
#     username = input('Enter your username: ')
#     user = cl.Client(username)
#     mainloop(user)


def sending(user):
    while True:
        message = input('[{}]: '.format(user.name))
        user.send_message(message)
        if message == '!exit':
            sys.exit()


def receiving(user):
    while True:
        message = user.get_message()
        if message:
            print(message)


def test():
    command = input('Run server on your computer? [Y/N] ')
    if command.lower() == 'y':
        server = sv.Server()
        server.run()
    else:
        username = input('Enter you name: ')
        user = cl.Client(username)
        user.connect()

        first = threading.Thread(target=sending, args=(user,))
        second = threading.Thread(target=receiving, args=(user,))

        first.start()
        second.start()


if __name__ == '__main__':
    test()
