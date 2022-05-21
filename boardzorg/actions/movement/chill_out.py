from copy import deepcopy

from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.actions import args
from boardzorg.actions.common import check_no_allies


class ActivateFrendsAndRaletions(Action):
    name = "activate-frends_and_raletions"
    ck_faction = "rabbit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round not in ["bidding", "retrieval", "movement"]:
            raise IllegalAction("Cannot activate frends_and_raletions right now") 
        if game_state.round == "movement":
            if game_state.round_state.imagine_has_sailed:
                raise IllegalAction("This imagine has already sailed")
        can_activate = False
        for space in game_state.map_state:
            if game_state.map_state[space].chill_out:
                can_activate = True
        if not can_activate:
            raise IllegalAction("Nowhere to activate frends_and_raletions")

    @classmethod
    def parse_args(cls, faction, args):
        space = args
        return ActivateFrendsAndRaletions(faction, space)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Space()

    def __init__(self, faction, space):
        self.faction = faction
        self.space = space

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        space = new_game_state.map_state[self.space]
        check_no_allies(game_state, self.faction, space)

        if "rabbit" not in space.forces:
            raise BadCommand("No forces to activate")
        if not space.chill_out:
            raise BadCommand("No frends_and_raletions to activate")
        space.chill_out = False
        return new_game_state


class AdviseIntruders(Action):
    name = "advise-intruders"
    ck_pause_context = ["flip-to-frends_and_raletions"]
    ck_faction = "rabbit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.query_flip_to_frends_and_raletions is None:
            raise IllegalAction("No intruders to advise")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space_name = new_game_state.query_flip_to_frends_and_raletions
        new_game_state.map_state[space_name].chill_out = True
        new_game_state.query_flip_to_frends_and_raletions = None
        new_game_state.pause_context = None
        return new_game_state


class PassAdviseIntruders(Action):
    name = "remain-hostile-to-intruders"
    ck_pause_context = ["flip-to-frends_and_raletions"]
    ck_faction = "rabbit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.query_flip_to_frends_and_raletions is None:
            raise IllegalAction("No intruders to advise")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.query_flip_to_frends_and_raletions = None
        new_game_state.pause_context = None
        return new_game_state


class SneakyActivateFighters(Action):
    name = "become-hostile"
    ck_pause_context = ["flip-to-fighters"]
    ck_faction = "rabbit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.query_flip_to_fighters is None:
            raise IllegalAction("No hostility is coming your way")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space_name = new_game_state.query_flip_to_fighters
        new_game_state.map_state[space_name].chill_out = False
        new_game_state.query_flip_to_fighters = None
        new_game_state.pause_context = None
        return new_game_state


class PassSneakyActivateFighters(Action):
    name = "remain-frends_and_raletions"
    ck_pause_context = ["flip-to-fighters"]
    ck_faction = "rabbit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.query_flip_to_fighters is None:
            raise IllegalAction("No hostility is coming your way anyway")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.query_flip_to_fighters = None
        new_game_state.pause_context = None
        return new_game_state
