

class Args:
    def to_dict(self):
        return {"widget": "null"}


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
    def __init__(self, min=0, max=100, type=None):
        self.min = min
        self.max = max
        self.type = type

    def to_dict(self):
        return {
            "widget": "integer",
            "args": {
                "min": self.min,
                "max": self.max,
                "type": self.type
            }
        }


class Spice(Integer):
    def __init__(self):
        super().__init__(min=0, type="spice")


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
    def __init__(self, faction=None):
        self.fedaykin = faction == "fremen"
        self.sardaukar = faction == "emperor"
    def to_dict(self):
        return {
            "widget": "units",
            "args": {
                "fedaykin": self.fedaykin,
                "sardaukar": self.sardaukar
            }
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
            "widget": "space-sector-select-start"
        }


class SpaceSectorStart(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select-start"
        }

class SpaceSectorEnd(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select-end"
        }


class FremenPlacementSelector(Args):
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
    def __init__(self):
        super().__init__(self, min=0, max=10)


class Token(Integer):
    def to_dict(self):
        return {
            "widget": "token-select"
        }
