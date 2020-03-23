

class Args:
    def to_dict(self):
        return {"widget": "input"}


class Union(Args):
    def __init__(self, *args):
        self.args = args

    def to_dict(self):
        return {
            "widget": "choice",
            "args": [a.to_dict() for a in self.args]
        }


class Struct(Args):
    def __init__(self, *args):
        self.args = args

    def to_dict(self):
        return {
            "widget": "struct",
            "args": [a.to_dict() for a in self.args]
        }


class Array(Args):
    def __init__(self, element_type):
        self.type = element_type

    def to_dict(self):
        return {
            "widget": "array",
            "args": self.type.to_dict()
        }


class String(Args):
    def to_dict(self):
        return {
            "widget": "input"
        }


class Integer(Args):
    def to_dict(self):
        return {
            "widget": "integer"
        }


class Spice(Integer):
    def to_dict(self):
        return {
            "widget": "integer",
            "args": {
                "min": 0,
                "type": "spice"
            }
        }


class Constant(Args):
    def __init__(self, constant):
        self.constant = constant

    def to_dict(self):
        return {
            "widget": "constant",
            "args": self.constant
        }


class Leader(String):
    def to_dict(self):
        return {
            "widget": "leader-input"
        }


class Units(Args):
    def to_dict(self):
        return {
            "widget": "units"
        }


class Space(String):
    def to_dict(self):
        return {
            "widget": "space-select"
        }


class Sector(Integer):
    def to_dict(self):
        return {
            "widget": "sector-select"
        }


class SpaceSector(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select"
        }


class FremenPlacementSpaceSector(SpaceSector):
    def to_dict(self):
        return {
            "widget": "fremen-placement-select"
        }


class Faction(String):
    def to_dict(self):
        return {
            "widget": "faction-select"
        }


class Turn(Integer):
    def to_dict(self):
        return {
            "widget": "integer",
            "args": {
                "min": 0,
                "max": 10
            }
        }


class Token(Integer):
    def to_dict(self):
        return {
            "widget": "token-select"
        }
