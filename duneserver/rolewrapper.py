import json
import string
import random


class RoleException(Exception):
    pass


def _random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def serialize(roles):
    return json.dumps(roles)


def realize(roles):
    return json.loads(roles)


def new():
    return {}


def assign(roles, role):
    if role in roles.values():
        raise Exception("Role already defined")

    key = _random_generator()
    roles[key] = role
    return key


def look_up(roles, key):
    if key not in roles:
        raise RoleException("Key not found")

    return roles[key]
