from copy import deepcopy

from dune.actions import args
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.actions.revival import parse_revival_units, parse_revival_leader
from dune.actions.revival import revive_units, revive_leader
from dune.map.map import MapGraph
from dune.actions.battle import ops
from dune.actions.storm import do_storm_round


def discard_treachery(game_state, faction, treachery):
    game_state.faction_state[faction].treachery.remove(treachery)
    game_state.treachery_discard.insert(0, treachery)


class TruthTrance(Action):
    name = "truth-trance"
    ck_treachery = "Truth-Trance"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.pause.append(self.faction)
        discard_treachery(new_game_state, self.faction, "Truth-Trance")
        return new_game_state


class TleilaxuGhola(Action):
    name = "tleilaxu-ghola"
    ck_treachery = "Tleilaxu-Ghola"

    @classmethod
    def parse_args(cls, faction, args):
        if not args:
            return TleilaxuGhola(faction, [], None)
        if "1" in args or "2" in args:
            units = args
            leader = ""
        else:
            leader = args
            units = ""
        return TleilaxuGhola(faction, parse_revival_units(units), parse_revival_leader(leader))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Union(
            args.RevivalUnits(game_state.faction_state[faction].tank_units, max_units=5, single_2=False),
            args.RevivalLeader(game_state.faction_state[faction].tank_leaders)
        )

    def __init__(self, faction, units, leader):
        self.faction = faction
        self.units = units
        self.leader = leader

    @classmethod
    def _check(cls, game_state, faction):
        if (not game_state.faction_state[faction].tank_units) and \
           game_state.faction_state[faction].tank_leaders:
            raise IllegalAction("You don't have anything to revive")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if self.leader and self.units:
            raise BadCommand("You must pick units or a leader")

        if self.leader:
            if self.leader not in new_game_state.faction_state[self.faction].tank_leaders:
                raise BadCommand("That leader is not revivable")
            revive_leader(self.leader, self.faction, new_game_state)

        if self.units:
            if len(self.units) > 5:
                raise BadCommand("You can only revive up to five units")
            revive_units(self.units, self.faction, new_game_state)

        discard_treachery(new_game_state, self.faction, "Tleilaxu-Ghola")
        return new_game_state


class FamilyAtomics(Action):
    name = "family-atomics"
    ck_treachery = "Family-Atomics"
    ck_round = "control"

    @classmethod
    def _check(cls, game_state, faction):
        someone_close = False
        m = MapGraph()
        for space in game_state.map_state.values():
            if faction in space.forces:
                for sector in space.forces[faction]:
                    if m.distance(space.name, sector, "Shield-Wall", 7) <= 1:
                        someone_close = True
                        break
                    if m.distance(space.name, sector, "Shield-Wall", 8) <= 1:
                        someone_close = True
                        break

        if not someone_close:
            raise IllegalAction("You cannot get to the shield wall")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.shield_wall = False

        ops.tank_all_units(new_game_state, "Shield-Wall")

        discard_treachery(new_game_state, self.faction, "Family-Atomics")
        return new_game_state


class WeatherControl(Action):
    name = "weather-control"
    ck_round = "storm"
    ck_treachery = "Weather-Control"

    @classmethod
    def parse_args(cls, faction, args):
        return WeatherControl(faction, int(args))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Integer(min=0, max=10)

    def __init__(self, faction, advance):
        self.faction = faction
        self.advance = advance

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.storm_deck.pop(0)
        do_storm_round(new_game_state, self.advance)
        discard_treachery(new_game_state, self.faction, "Weather-Control")
        return new_game_state


class PassWeatherControl(Action):
    name = "pass-weather-control"
    ck_round = "storm"
    ck_treachery = "Weather-Control"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        do_storm_round(new_game_state, new_game_state.storm_deck.pop(0))
        return new_game_state
