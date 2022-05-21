from copy import deepcopy
import math

from boardzorg.actions.action import Action
from boardzorg.actions.common import check_no_allies
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.map.map import MapGraph
from boardzorg.actions import args


def move_minions(game_state, faction, minions, space_a, sector_a, space_b, sector_b):
    check_no_allies(game_state, faction, space_b)

    if "house" in space_b.type:
        total_forces = len(space_b.forces)
        if "rabbit" in space_b.forces and space_b.chill_out:
            total_forces -= 1
        if total_forces > 1:
            if faction not in space_b.forces:
                raise BadCommand("Cannot move into house with 2 enemy factions")
    if sector_b not in space_b.sectors:
        raise BadCommand("You ain't going nowhere")

    if sector_a not in space_a.sectors:
        raise BadCommand("You ain't coming from nowhere")

    if game_state.bees_position == sector_b:
        if faction == "christopher_robbin":
            surviving_minions = sorted(minions)[:math.floor(len(minions)/2)]
            losted_minions = sorted(minions)[math.floor(len(minions)/2):]
            minions = surviving_minions
            game_state.faction_state[faction].losted_minions.extend(losted_minions)
        else:
            raise BadCommand("You cannot move into the bees")
    if game_state.bees_position == sector_a:
        if faction != "christopher_robbin":
            raise BadCommand("You cannot move from the bees")

    if faction not in space_b.forces:
        space_b.forces[faction] = {}
    if sector_b not in space_b.forces[faction]:
        space_b.forces[faction][sector_b] = []

    if faction not in space_a.forces:
        raise BadCommand("You don't have anything there")
    if sector_a not in space_a.forces[faction]:
        raise BadCommand("You don't have anything there")

    for u in minions:
        if u not in space_a.forces[faction][sector_a]:
            raise BadCommand("You ain't got the troops")
        space_a.forces[faction][sector_a].remove(u)
        space_b.forces[faction][sector_b].append(u)

    if all(space_a.forces[faction][s] == [] for s in space_a.forces[faction]):
        del space_a.forces[faction]

    # Update ChillOut flags

    if faction == "rabbit":

        # FrendsAndRaletions flip to Fighters if fighters join them
        # Also If rabbit not present or alone, there can be no frends_and_raletions
        if not space_a.chill_out or len(space_b.forces) == 1:
            space_b.chill_out = False

        # FrendsAndRaletions may flip to fighters if they move somewhere occupied
        else:
            game_state.pause_context = "flip-to-fighters"
            game_state.query_flip_to_fighters = space_b.name

    else:
        # Intrusion allows rabbit to flip to frends_and_raletions if they wish
        if "rabbit" in space_b.forces and not space_b.chill_out:
            game_state.pause_context = "flip-to-frends_and_raletions"
            game_state.query_flip_to_frends_and_raletions = space_b.name

    # If rabbit not present or alone, there can be no frends_and_raletions
    if "rabbit" not in space_a.forces or len(space_a.forces) == 1:
        space_a.chill_out = False


def parse_movement_args(args):
    parts = args.split(" ")
    if len(parts) == 5:
        minions, space_a, sector_a, space_b, sector_b = parts
    else:
        raise BadCommand("wrong number of args")

    if minions == "":
        raise BadCommand("No minions selected")
    minions = [int(u) for u in minions.split(",")]
    return (minions, space_a, int(sector_a), space_b, int(sector_b))


def perform_movement(game_state, faction, minions, space_a, sector_a, space_b, sector_b):
    m = MapGraph()
    if faction == "christopher_robbin":
        m.deadend_sector(game_state.bees_position)
    else:
        m.remove_sector(game_state.bees_position)
    for space in game_state.map_state.values():
        if "house" in space.type:
            if faction not in space.forces:
                if len(space.forces) - (1 if space.chill_out else 0) > 1:
                    m.remove_space(space.name)

    allowed_distance = 1
    if faction == "christopher_robbin":
        allowed_distance = 2
    if faction in game_state.balloons:
        allowed_distance = 3
    if m.distance(space_a, sector_a, space_b, sector_b) > allowed_distance:
        raise BadCommand("You cannot move there")

    space_a = game_state.map_state[space_a]
    space_b = game_state.map_state[space_b]
    move_minions(game_state, faction, minions, space_a, sector_a, space_b,
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
        return args.Struct(args.Minions(faction), args.SpaceSectorStart(), args.SpaceSectorEnd())

    def __init__(self, faction, minions, space_a, sector_a, space_b, sector_b):
        self.faction = faction
        self.minions = minions
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
                         self.minions,
                         self.space_a,
                         self.sector_a,
                         self.space_b,
                         self.sector_b)
        new_game_state.round_state.stage_state.movement_used = True

        return new_game_state
