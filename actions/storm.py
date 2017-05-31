from copy import deepcopy
from random import randint

from actions.action import Action

from state.state import SpiceState


def destroy_in_path(game_state, sectors):
    for space in game_state.board_state.map_state.values():
        if not set(space.sectors).isdisjoint(set(sectors)):
            if space.type == "sand" or ("protected" in space.type and not game_state.board_state.shield_wall):
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


class Storm(Action):
    name = "storm"
    ck_round = "storm"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        advance = new_game_state.board_state.storm_advance

        new_game_state.board_state.storm_position = (new_game_state.board_state.storm_position + advance) % 12

        new_game_state.board_state.storm_advance = randint(1, 6)

        destroy_in_path(new_game_state,
                        range(game_state.board_state.storm_position, new_game_state.board_state.storm_position))

        new_game_state.round_state = SpiceState()

        return new_game_state
