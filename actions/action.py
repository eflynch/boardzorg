from exceptions import IllegalAction


class ActionMeta(type):
    def __init__(cls, name, bases, dct):
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        else:
            if not hasattr(cls, 'ck_round'):
                cls.registry[cls.name] = cls

        if not hasattr(cls, 'round_registry'):
            cls.round_registry = {}
        else:
            if hasattr(cls, 'ck_round'):
                if cls.ck_round not in cls.round_registry:
                    cls.round_registry[cls.ck_round] = {}
                cls.round_registry[cls.ck_round][cls.name] = cls

        super(ActionMeta, cls).__init__(name, bases, dct)


class Action(object, metaclass=ActionMeta):
    name = "nop"
    su = False

    def __repr__(self):
        return self.name

    @classmethod
    def parse_args(cls, faction, args):
        return cls(faction)

    @classmethod
    def check_turn(cls, game_state, faction):
        if game_state.round_state.faction_turn != faction:
            raise IllegalAction("Cannot do that when it's not your turn")

    @classmethod
    def check_alliance(self, game_state, faction, ally):
        if faction == ally:
            return True
        if ally in game_state.alliances[faction]:
            return True
        return False

    @classmethod
    def check(cls, game_state, faction):
        if hasattr(cls, "ck_round"):
            if game_state.round_state.round != cls.ck_round:
                raise IllegalAction("Cannot do that in this round")
        if hasattr(cls, "ck_faction"):
            if faction != cls.ck_faction:
                raise IllegalAction("Only {} can {}".format(cls.ck_faction, cls.name))
        if cls.su and faction is not None:
            raise IllegalAction("Only God can do that")
        if not cls.su and faction is None:
            raise IllegalAction("God cannot do that")

        if hasattr(cls, "_check"):
            cls._check(game_state, faction)

    def __init__(self, faction=None):
        self.faction = faction

    def execute(self, game_state):
        self.check(game_state, self.faction)
        if self._execute is None:
            return game_state
        return self._execute(game_state)
