

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


class Hunny(Integer):
    def __init__(self):
        super(Hunny, self).__init__(min=0, type="hunny")


class Constant(Args):
    def __init__(self, constant):
        self.constant = constant

    def to_dict(self):
        return {
            "widget": "constant",
            "args": self.constant
        }


class TraitorCharacter(String):
    def to_dict(self):
        return {
            "widget": "traitor-select",
        }


class Character(String):
    def to_dict(self):
        return {
            "widget": "character-input"
        }


class Minions(Args):
    def __init__(self, faction=None):
        self.woozles = faction == "christopher_robbin"
        self.very_sad_boys = faction == "eeyore"

    def to_dict(self):
        return {
            "widget": "minions",
            "args": {
                "woozles": self.woozles,
                "very_sad_boys": self.very_sad_boys
            }
        }


class RetrievalMinions(Args):
    def __init__(self, minions, max_minions=3, single_2=True, title=None):
        self.minions = minions
        self.max_minions = max_minions
        self.single_2 = single_2
        self.title = title

    def to_dict(self):
        return {
            "widget": "retrieval-minions",
            "args": {
                "minions": self.minions,
                "title": self.title,
                "maxMinions": self.max_minions,
                "single2": self.single_2,
            }
        }


class RetrievalCharacter(Args):
    def __init__(self, characters, required=False):
        self.characters = characters
        self.required = required

    def to_dict(self):
        return {
            "widget": "retrieval-character",
            "args": {
                "characters": self.characters,
                "required": self.required,
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
            "widget": "space-sector-select-start",
            "args": {}
        }


class SpaceSectorStart(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select-start",
            "args": {}
        }


class SpaceSectorEnd(Args):
    def to_dict(self):
        return {
            "widget": "space-sector-select-end",
            "args": {}
        }


class ChristopherRobbinPlacementSelector(Args):
    def to_dict(self):
        return {
            "widget": "christopher_robbin-placement-select"
        }


class Battle(Args):
    def to_dict(self):
        return {
            "widget": "battle-select"
        }


class BattlePlan(Args):
    def __init__(self, faction, max_power):
        self.faction = faction
        self.max_power = max_power

    def to_dict(self):
        return {
            "widget": "battle-plan",
            "args": {
                "faction": self.faction,
                "max_power": self.max_power
            }
        }


class Faction(String):
    def to_dict(self):
        return {
            "widget": "faction-select"
        }


class MultiFaction(String):
    def __init__(self, factions):
        self.factions = factions

    def to_dict(self):
        return {
            "widget": "multi-faction-select",
            "args": {
                "factions": list(self.factions)
            }
        }


class Flight(Args):
    def to_dict(self):
        return {
            "widget": "flight"
        }


class FlightAnswer(Args):
    def __init__(self, max_power):
        self.max_power = max_power

    def to_dict(self):
        return {
            "widget": "flight-answer",
            "args": {
                "max_power": self.max_power
            }
        }


class Cleverness(Args):
    def to_dict(self):
        return {
            "widget": "cleverness"
        }


class LostMinions(Args):
    def to_dict(self):
        return {
            "widget": "lost-minions"
        }


class DiscardProvisions(Args):
    def to_dict(self):
        return {
            "widget": "discard-provisions"
        }


class ReturnProvisions(Args):
    def __init__(self, number):
        self.number = number

    def to_dict(self):
        return {
            "widget": "return-provisions",
            "args": {
                "number": self.number
            }
        }


class Turn(Integer):
    def __init__(self):
        super(Turn, self).__init__(min=0, max=10)


class Token(Integer):
    def to_dict(self):
        return {
            "widget": "token-select"
        }
