from copy import deepcopy

from dune.actions.action import Action


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
