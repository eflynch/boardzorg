from copy import deepcopy
from random import randint

from dune.actions.action import Action

TOKEN_SECTORS = [1, 4, 7, 10, 13, 16]


def destroy_in_path(game_state, sectors):
    for space in game_state.map_state.values():
        if not set(space.sectors).isdisjoint(set(sectors)):
            if space.type == "sand" or ("protected" in space.type and not game_state.shield_wall):
                for s in set(space.sectors) & set(sectors):
                    for faction in space.forces:
                        space.forces[faction][s]
                        if "fremen" in space.forces:
                            was = space.forces["fremen"][s]
                            space.forces["fremen"][s] = sorted(was)[:len(was)/2]
                        else:
                            space.forces[faction][s] = []
                    if s == space.spice_sector:
                        space.spice = 0


def get_faction_order(game_state):
    faction_order = []
    storm_position = game_state.storm_position
    for i in range(18):
        sector = (storm_position + i + 1) % 18
        if sector in TOKEN_SECTORS:
            for f in game_state.faction_state:
                faction_state = game_state.faction_state[f]
                if faction_state.token_position == sector:
                    faction_order.append(f)
    return faction_order


class Storm(Action):
    name = "storm"
    ck_round = "storm"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        advance = new_game_state.storm_advance

        new_game_state.storm_position = (new_game_state.storm_position + advance) % 12

        new_game_state.storm_advance = randint(1, 6)

        destroy_in_path(new_game_state,
                        range(game_state.storm_position, new_game_state.storm_position))

        new_game_state.round = "spice"

        return new_game_state
