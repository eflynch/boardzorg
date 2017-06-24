from copy import deepcopy

from dune.actions.action import Action
from dune.map.map import MapGraph


class DoCollection(Action):
    name = "do-collection"
    ck_round = "collection"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        m = MapGraph()
        m.remove_sector(new_game_state.storm_position)

        for space in new_game_state.map_state.values():
            if not space.spice or not space.forces:
                continue

            for faction in space.forces:
                collection_rate = 2
                if faction in new_game_state.ornithopters:
                    collection_rate = 3
                sectors = space.forces[faction]
                for s in sectors:
                    if m.distance(space.name, s, space.name, space.spice_sector) == 0:
                        num_units = len(sectors[s])
                        spice_collected = min(space.spice, num_units * collection_rate)
                        new_game_state.faction_state[faction].spice += spice_collected
                        space.spice -= spice_collected

        new_game_state.round = "control"
        return new_game_state
