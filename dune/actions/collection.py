from copy import deepcopy

from dune.actions.action import Action


class StartCollection(Action):
    name = "start-collection"
    ck_round = "collection"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        return new_game_state
