from boardzorg.exceptions import IllegalAction
from boardzorg.actions.args import Args
from boardzorg.state.provisions_cards import WORTHLESS


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
    def get_arg_spec(cls, faction=None, game_state=None):
        return Args()

    @classmethod
    def check_author(cls, game_state, faction, exception=None):
        if faction is None:
            raise IllegalAction("Got to be someone to do this")

        if game_state.author_context[faction] is not None:
            if (not hasattr(cls, "ck_author_context")) or game_state.author_context[faction] not in cls.ck_author_context:
                if exception is None:
                    raise IllegalAction("Author is spoken for")
                else:
                    raise exception

        is_bene = faction == "rabbit"
        has_author = "Author" in game_state.faction_state[faction].provisions
        worthless_count = sum([1 for card in game_state.faction_state[faction].provisions if card in WORTHLESS])
        if is_bene:
            if not has_author and worthless_count == 0:
                if exception is None:
                    raise IllegalAction("You need a Author card or Worthless card")
                else:
                    raise exception
        else:
            if not has_author:
                if exception is None:
                    raise IllegalAction("You need a Author card")
                else:
                    raise exception

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
    def get_is_blocking(cls):
        if hasattr(cls, "non_blocking"):
            return False
        return True

    @classmethod
    def get_action(cls, action_name):
        if action_name in cls.registry:
            return cls.registry[action_name]
        return None

    @classmethod
    def check_faction_author(cls, game_state, faction):
        if game_state.faction_state[faction].used_faction_author:
            raise IllegalAction(f"{faction} must have not used their faction author power")

    @classmethod
    def check(cls, game_state, faction):
        if game_state.round == "end":
            raise IllegalAction("There are no actions left")
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
        if hasattr(cls, "ck_author"):
            cls.check_author(game_state, faction) 
        if hasattr(cls, "ck_faction_author"):
            if faction != cls.ck_faction_author:
                raise IllegalAction("Only {} can {}".format(cls.ck_faction_author, cls.name))
            cls.check_faction_author(game_state, faction)
        if hasattr(cls, "ck_provisions"):
            if faction not in game_state.faction_state:
                raise IllegalAction("You can't be doing that")
            if cls.ck_provisions not in game_state.faction_state[faction].provisions:
                raise IllegalAction("Cannot use a card you don't have")
        if game_state.pause_context is not None:
            if not hasattr(cls, "ck_pause_context"):
                raise IllegalAction("Global pause context in effect")
            else:
                if game_state.pause_context not in cls.ck_pause_context:
                    raise IllegalAction(
                        "Global pause context {} in effect".format(game_state.pause_context))

        if cls.su and faction is not None:
            raise IllegalAction("Only God can do that")
        if not cls.su and faction is None:
            raise IllegalAction("God cannot do that")

        if cls.su and game_state.pause:
            raise IllegalAction("Wait for players to accept pause.")

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
from boardzorg.actions import setup, bees, hunny, picnick, bidding, provisions  # noqa # pylint: disable=unused-import
from boardzorg.actions import retrieval, movement, battle, collection, control  # noqa # pylint: disable=unused-import
