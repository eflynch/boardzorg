from dune.exceptions import IllegalAction


class ActionMeta(type):
    def __init__(cls, name, bases, dct):
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        else:
            if cls.name in cls.registry:
                raise Exception("Non-unique action name {}".format(cls.name))
            cls.registry[cls.name] = cls

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
    def check_alliance(cls, game_state, faction, ally):
        if faction == ally:
            return True
        if ally in game_state.alliances[faction]:
            return True
        raise IllegalAction("You must be allies with the {}".format(ally))

    @classmethod
    def get_valid_actions(cls, game_state, faction):
        valid_actions = {}
        for action in cls.registry:
            try:
                cls.registry[action].check(game_state, faction)
            except IllegalAction:
                pass
            else:
                valid_actions[action] = cls.registry[action]

        return valid_actions

    @classmethod
    def get_action(cls, action_name):
        if action_name in cls.registry:
            return cls.registry[action_name]
        return None

    @classmethod
    def check(cls, game_state, faction):
        if hasattr(cls, "ck_round"):
            if game_state.round != cls.ck_round:
                raise IllegalAction("Cannot do that in this round")
        if hasattr(cls, "ck_stage"):
            if game_state.round_state.stage != cls.ck_stage:
                raise IllegalAction("Cannot do that in this stage")
        if hasattr(cls, "ck_substage"):
            if game_state.round_state.stage_state.substage != cls.ck_substage:
                raise IllegalAction("Cannot do that in this substage")
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


# These unsed imports register the Action classes
from dune.actions import setup, storm, spice, nexus, bidding  # noqa # pylint: disable=unused-import
from dune.actions import revival, movement, battle, collection, control   # noqa # pylint: disable=unused-import
