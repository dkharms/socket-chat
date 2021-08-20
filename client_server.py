class ClientServer:
    def __init__(self, id, name, sock):
        self.id = id
        self.name = name
        self.sock = sock

        self.connected = True
        self.room = None

    def set_room(self, room):
        self.room = room

    def is_host(self):
        return self.room and self.room.host.id == self.id

    def disconnect(self):
        self.connected = False
        if self.room:
            self.room.delete_user(self)
        self.sock.close()
