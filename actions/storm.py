from copy import deepcopy
from random import randint

from actions.action import Action

from state import SpiceState


class Storm(Action):
    def __init__(self):
        pass

    def _destroy_path(self, game_state, sectors):
        for space in game_state.board_state.map_state.values():
            if not set(space.sectors).isdisjoint(sectors):
                space_is_fucked = True
                if space.is_stronghold or space.is_rock:
                    space_is_fucked = False
                if space.is_protected_by_shieldwall and not game_state.board_state.shield_wall:
                    space_is_fucked = True

                if space_is_fucked:
                    if "fremen" in space.forces:
                        space.forces = {
                            "fremen": sorted(space.forces["fremen"])[:len(space.forces["fremen"])/2]
                        }
                    else:
                        space.forces = {}
                    space.spice = 0

    def execute(self, game_state):
        new_game_state = deepcopy(game_state)

        advance = new_game_state.board_state.storm_advance

        new_game_state.board_state.storm_position = (new_game_state.board_state.storm_position + advance) % 12

        new_game_state.board_state.storm_advance = randint(1, 6)

        self._destroy_path(new_game_state, set(range(game_state.board_state.storm_position,
                                                     new_game_state.board_state.storm_position)))

        new_game_state.round_state = SpiceState()

        return new_game_state
