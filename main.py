import client as cl
import server as sv

server = None


def mainloop(user):
    message = input('[MESSAGE]: ')
    if message.startswith('!'):
        process_command(message[1:], user)
    else:
        user.send_message(message)


def main():
    global server
    command = input('Run server on your computer? [Y/N] ')
    if command.lower() == 'y':
        server = sv.Server()

    username = input('Enter your username: ')
    user = cl.Client(username)
    mainloop(user)


if __name__ == '__main__':
    main()
