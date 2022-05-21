from copy import deepcopy

from boardzorg.actions.action import Action
from boardzorg.map.map import MapGraph
from boardzorg.exceptions import IllegalAction, BadCommand


class Continue(Action):
    name = "continue"

    @classmethod
    def _check(cls, game_state, faction):
        if faction not in game_state.pause:
            raise IllegalAction("Cannot continue if you are not one of the pausers")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.pause.remove(self.faction)
        return new_game_state


class DoCollection(Action):
    name = "do-collection"
    ck_round = "collection"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        m = MapGraph()
        m.remove_sector(new_game_state.bees_position)

        for space in new_game_state.map_state.values():
            if not space.hunny or not space.forces:
                continue

            for faction in space.forces:
                if faction == "rabbit" and space.chill_out:
                    continue
                collection_rate = 2
                if faction in new_game_state.balloons:
                    collection_rate = 3
                sectors = space.forces[faction]
                for s in sectors:
                    if m.distance(space.name, s, space.name, space.hunny_sector) == 0:
                        num_minions = len(sectors[s])
                        hunny_collected = min(space.hunny, num_minions * collection_rate)
                        new_game_state.faction_state[faction].hunny += hunny_collected
                        space.hunny -= hunny_collected

        new_game_state.round = "control"
        new_game_state.pause = list(game_state.faction_state.keys())
        return new_game_state
