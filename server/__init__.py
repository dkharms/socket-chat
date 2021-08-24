class IdField:

    def __init__(self):
        self.value = 0

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        id = self.value
        self.value += 1

        return id
