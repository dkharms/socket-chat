class Room:

    def __init__(self, id, host, name, password=None):
        self.id = id
        self.host = host
        self.name = name
        self.password = password
        self.participants = [host]

    def add_user(self, user):
        self.participants.append(user)
        user.set_room(self)

    def delete_user(self, username):
        user = filter(lambda x: x.name == username, self.participants)
        if user:
            self.participants.remove(user)

    def __eq__(self, other):
        return self.id == other.id
