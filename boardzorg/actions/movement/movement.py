from copy import deepcopy
import math

from boardzorg.actions.action import Action
from boardzorg.actions.common import check_no_allies
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.map.map import MapGraph
from boardzorg.actions import args


def move_units(game_state, faction, units, space_a, sector_a, space_b, sector_b):
    check_no_allies(game_state, faction, space_b)

    if "stronghold" in space_b.type:
        total_forces = len(space_b.forces)
        if "bene-gesserit" in space_b.forces and space_b.coexist:
            total_forces -= 1
        if total_forces > 1:
            if faction not in space_b.forces:
                raise BadCommand("Cannot move into stronghold with 2 enemy factions")
    if sector_b not in space_b.sectors:
        raise BadCommand("You ain't going nowhere")

    if sector_a not in space_a.sectors:
        raise BadCommand("You ain't coming from nowhere")

    if game_state.storm_position == sector_b:
        if faction == "fremen":
            surviving_units = sorted(units)[:math.floor(len(units)/2)]
            tanked_units = sorted(units)[math.floor(len(units)/2):]
            units = surviving_units
            game_state.faction_state[faction].tanked_units.extend(tanked_units)
        else:
            raise BadCommand("You cannot move into the storm")
    if game_state.storm_position == sector_a:
        if faction != "fremen":
            raise BadCommand("You cannot move from the storm")

    if faction not in space_b.forces:
        space_b.forces[faction] = {}
    if sector_b not in space_b.forces[faction]:
        space_b.forces[faction][sector_b] = []

    if faction not in space_a.forces:
        raise BadCommand("You don't have anything there")
    if sector_a not in space_a.forces[faction]:
        raise BadCommand("You don't have anything there")

    for u in units:
        if u not in space_a.forces[faction][sector_a]:
            raise BadCommand("You ain't got the troops")
        space_a.forces[faction][sector_a].remove(u)
        space_b.forces[faction][sector_b].append(u)

    if all(space_a.forces[faction][s] == [] for s in space_a.forces[faction]):
        del space_a.forces[faction]

    # Update Coexist flags

    if faction == "bene-gesserit":

        # Advisors flip to Fighters if fighters join them
        # Also If bene-gesserit not present or alone, there can be no advisors
        if not space_a.coexist or len(space_b.forces) == 1:
            space_b.coexist = False

        # Advisors may flip to fighters if they move somewhere occupied
        else:
            game_state.pause_context = "flip-to-fighters"
            game_state.query_flip_to_fighters = space_b.name

    else:
        # Intrusion allows bene-gesserit to flip to advisors if they wish
        if "bene-gesserit" in space_b.forces and not space_b.coexist:
            game_state.pause_context = "flip-to-advisors"
            game_state.query_flip_to_advisors = space_b.name

    # If bene-gesserit not present or alone, there can be no advisors
    if "bene-gesserit" not in space_a.forces or len(space_a.forces) == 1:
        space_a.coexist = False


def parse_movement_args(args):
    parts = args.split(" ")
    if len(parts) == 5:
        units, space_a, sector_a, space_b, sector_b = parts
    else:
        raise BadCommand("wrong number of args")

    if units == "":
        raise BadCommand("No units selected")
    units = [int(u) for u in units.split(",")]
    return (units, space_a, int(sector_a), space_b, int(sector_b))


def perform_movement(game_state, faction, units, space_a, sector_a, space_b, sector_b):
    m = MapGraph()
    if faction == "fremen":
        m.deadend_sector(game_state.storm_position)
    else:
        m.remove_sector(game_state.storm_position)
    for space in game_state.map_state.values():
        if "stronghold" in space.type:
            if faction not in space.forces:
                if len(space.forces) - (1 if space.coexist else 0) > 1:
                    m.remove_space(space.name)

    allowed_distance = 1
    if faction == "fremen":
        allowed_distance = 2
    if faction in game_state.ornithopters:
        allowed_distance = 3
    if m.distance(space_a, sector_a, space_b, sector_b) > allowed_distance:
        raise BadCommand("You cannot move there")

    space_a = game_state.map_state[space_a]
    space_b = game_state.map_state[space_b]
    move_units(game_state, faction, units, space_a, sector_a, space_b,
               sector_b)


class Move(Action):
    name = "move"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        return Move(faction, *parse_movement_args(args))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Units(faction), args.SpaceSectorStart(), args.SpaceSectorEnd())

    def __init__(self, faction, units, space_a, sector_a, space_b, sector_b):
        self.faction = faction
        self.units = units
        self.space_a = space_a
        self.space_b = space_b
        self.sector_a = sector_a
        self.sector_b = sector_b

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.stage_state.movement_used:
            raise IllegalAction("You have already moved this turn")

    def _execute(self, game_state):

        new_game_state = deepcopy(game_state)
        perform_movement(new_game_state,
                         self.faction,
                         self.units,
                         self.space_a,
                         self.sector_a,
                         self.space_b,
                         self.sector_b)
        new_game_state.round_state.stage_state.movement_used = True

        return new_game_state
