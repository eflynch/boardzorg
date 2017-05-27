from copy import deepcopy

from actions.action import Action

from exceptions import IllegalAction

from state import SpiceState


class ExitNexus(Action):
    def execute(self, game_state):
        new_game_state = deepcopy(game_state)

        space = new_game_state.board_state.shai_hulud

        space.forces = {}
        space.spice = 0
        new_game_state.board_state.shai_hulud = None
        new_game_state.round_state = SpiceState()

        return new_game_state


class WormRide(Action):
    def parse_args(faction, args):
        space, sector = args.split(" ")
        sector = int(sector)
        return WormRide(faction, space, sector)

    def __init__(self, faction, space, sector):
        self.faction = faction
        self.space = space
        self.sector = sector

    def execute(self, game_state):
        self.check_round(game_state, "nexus")
        new_game_state = deepcopy(game_state)

        if self.faction != "fremen":
            raise IllegalAction("Only Fremen can Ride Worms")

        if not new_game_state.round_state.alliance_stage_over:
            raise IllegalAction("People are still arguing about alliances")

        if new_game_state.round_state.fremen_movement_over:
            raise IllegalAction("The Fremen already rode a worm today")

        space = new_game_state.board_state.shai_hulud

        if "fremen" not in space.forces:
            raise IllegalAction("There are no Fremen to ride the worm")

        new_space = new_game_state.board_state.map_state[self.space]

        if "fremen" not in new_space.forces:
            new_space.forces["fremen"] = space.forces["fremen"]
        else:
            new_space.forces["fremen"].extend(space.forces["fremen"])

        del space.forces["fremen"]

        new_game_state.round_state.fremen_movement_over = True

        return new_game_state
