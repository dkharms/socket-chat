class Room:

    def __init__(self, room_id, host, name, password=None):
        self.room_id = room_id
        self.host = host
        self.name = name
        self.password = password
        self.participants = [host]

    def add_user(self, user):
        self.participants.append(user)
        user.set_room(self)

    def delete_user(self, client_id):
        print(self.participants)
        user = list(filter(lambda x: x.client_id == client_id, self.participants))
        if len(user) == 1:
            self.participants.remove(user[0])

    def __eq__(self, other):
        return self.room_id == other.room_id
