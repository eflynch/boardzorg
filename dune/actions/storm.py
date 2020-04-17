from copy import deepcopy
from random import randint

from dune.actions import args
from dune.actions.action import Action
from dune.actions.battle import ops
from dune.actions.treachery import discard_treachery
from dune.exceptions import IllegalAction


def destroy_in_path(game_state, sectors):
    for space in game_state.map_state.values():
        if not set(space.sectors).isdisjoint(set(sectors)):
            if space.type == "sand" or ("shielded" in space.type and not game_state.shield_wall):
                ops.tank_all_units(game_state, space.name, restrict_sectors=sectors, half_fremen=True)
                if space.spice_sector and space.spice_sector in sectors:
                    space.spice = 0


def do_storm_round(game_state, advance):
    game_state.storm_position = (game_state.storm_position + advance) % 18

    destroy_in_path(game_state,
                    range(game_state.storm_position, game_state.storm_position + 1))

    game_state.round = "spice"

    game_state.ornithopters = []
    carthag = game_state.map_state["Carthag"]
    arrakeen = game_state.map_state["Arrakeen"]
    if carthag.forces:
        game_state.ornithopters.append(list(carthag.forces.keys())[0])
    if arrakeen.forces:
        game_state.ornithopters.append(list(arrakeen.forces.keys())[0])


class Storm(Action):
    name = "storm"
    ck_round = "storm"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.weather_control_passes) != len(game_state.faction_state):
            raise IllegalAction("Weather control passes not complete, can't proceed as normal")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        do_storm_round(new_game_state, new_game_state.storm_deck.pop(0))
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

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.weather_control_passes:
            raise IllegalAction("Already passed, it's too late!")

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

    @classmethod
    def parse_args(cls, faction, args):
        return PassWeatherControl(faction)

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.weather_control_passes:
            raise IllegalAction("Already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.weather_control_passes.append(self.faction)
        return new_game_state
