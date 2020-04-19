from copy import deepcopy

from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.actions import args
from dune.actions.common import check_no_allies


class ActivateAdvisors(Action):
    name = "activate-advisors"
    ck_faction = "bene-gesserit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round not in ["bidding", "revival", "movement"]:
            raise IllegalAction("Cannot activate advisors right now") 
        if game_state.round == "movement":
            if game_state.round_state.ship_has_sailed:
                raise IllegalAction("This ship has already sailed")
        can_activate = False
        for space in game_state.map_state:
            if game_state.map_state[space].coexist:
                can_activate = True
        if not can_activate:
            raise IllegalAction("Nowhere to activate advisors")

    @classmethod
    def parse_args(cls, faction, args):
        space = args
        return ActivateAdvisors(faction, space)

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

        if "bene-gesserit" not in space.forces:
            raise BadCommand("No forces to activate")
        if not space.coexist:
            raise BadCommand("No advisors to activate")
        space.coexist = False
        return new_game_state


class AdviseIntruders(Action):
    name = "advise-intruders"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    ck_faction = "bene-gesserit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.query_flip_to_advisors is None:
            raise IllegalAction("No intruders to advise")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space_name = new_game_state.round_state.stage_state.query_flip_to_advisors
        new_game_state.map_state[space_name].coexist = True
        new_game_state.round_state.stage_state.query_flip_to_advisors = None
        return new_game_state


class PassAdviseIntruders(Action):
    name = "remain-hostile-to-intruders"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    ck_faction = "bene-gesserit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.query_flip_to_advisors is None:
            raise IllegalAction("No intruders to advise")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.query_flip_to_advisors = None
        return new_game_state


class SneakyActivateFighters(Action):
    name = "become-hostile"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    ck_faction = "bene-gesserit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.query_flip_to_fighters is None:
            raise IllegalAction("No hostility is coming your way")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space_name = new_game_state.round_state.stage_state.query_flip_to_fighters
        new_game_state.map_state[space_name].coexist = False
        new_game_state.round_state.stage_state.query_flip_to_fighters = None
        return new_game_state


class PassSneakyActivateFighters(Action):
    name = "remain-advisorial"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"
    ck_faction = "bene-gesserit"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.query_flip_to_fighters is None:
            raise IllegalAction("No hostility is coming your way anyway")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.query_flip_to_fighters = None
        return new_game_state

