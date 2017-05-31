
class Object:
    pass


def class_init(cls):
    print("getting inited")


Object.__init__ = class_init


class SubObject(Object):
    def __init__(self):
        print("again")


o = Object()
s = SubObject()
