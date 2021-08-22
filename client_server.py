class ClientServer:
    def __init__(self, client_id, name, sock, address):
        self.client_id = client_id
        self.name = name
        self.sock = sock
        self.address = address

        self.connected = True
        self.room = None

    def set_room(self, room):
        self.room = room

    def is_host(self):
        return self.room and self.room.host.client_id == self.client_id

    def disconnect(self):
        self.connected = False
        if self.room:
            self.room.delete_user(self.client_id)
        self.sock.close()
