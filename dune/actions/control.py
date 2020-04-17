from copy import deepcopy

from dune.actions.action import Action
from dune.state.rounds.storm import StormRound


VICTORY_MATRIX = {
    1: {1: 5},
    2: {1: 4},
    3: {1: 4, 2: 5},
    4: {1: 3, 2: 4, 3: 5},
    5: {1: 3, 2: 4, 3: 5, 4: 5},
    6: {1: 3, 2: 4, 3: 5, 4: 5, 5: 5}
}


class DoControl(Action):
    name = "do-control"
    ck_round = "control"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        # collect spice bribes
        for faction in new_game_state.faction_state:
            fs = new_game_state.faction_state[faction]
            if fs.bribe_spice:
                fs.spice += fs.bribe_spice
                fs.bribe_spice = 0

        stronghold_occupiers = {None: []}
        for space in new_game_state.map_state.values():
            if "stronghold" in space.type:
                if space.forces:
                    faction = list(space.forces.keys())[0]
                    if faction not in stronghold_occupiers:
                        stronghold_occupiers[faction] = []
                    stronghold_occupiers[faction].append(space.name)
                else:
                    stronghold_occupiers[None].append(space.name)

        alliances = []
        for faction in new_game_state.alliances:
            alliance = tuple(sorted(new_game_state.alliances[faction] | set([faction])))
            alliances.append(alliance)
        alliances = set(alliances)

        winner = None

        for a in alliances:
            strongholds = 0
            for faction in a:
                if faction in stronghold_occupiers:
                    strongholds += len(stronghold_occupiers[faction])
            if VICTORY_MATRIX[len(new_game_state.faction_state)][len(a)] <= strongholds:
                winner = a
                break

        if winner is None:
            if new_game_state.turn == 10:
                if "fremen" in new_game_state.faction_state:
                    tabr = new_game_state.map_state["Sietch-Tabr"]
                    habbanya = new_game_state.map_state["Habbanya-Sietch"]
                    tueks = new_game_state.map_state["Tueks-Sietch"]
                    if not tabr.forces or "fremen" in tabr.forces:
                        if not habbanya.forces or "fremen" in habbanya.forces:
                            if all(f not in tueks.forces for f in ["atreides", "harkonnen", "emperor"]):
                                winner = ("fremen",)

        if winner is None:
            if new_game_state.turn == 10:
                if "guild" in new_game_state.faction_state:
                    winner = ("guild",)

        if "bene-gesserit" in new_game_state.faction_state:
            faction, turn = new_game_state.faction_state["bene-gesserit"].prediction
            if new_game_state.turn == turn:
                if faction in a:
                    winner = ("bene-gesserit",)

        if winner is not None:
            new_game_state.winner = winner
            new_game_state.round = "end"
            return new_game_state

        new_game_state.round_state = StormRound()
        return new_game_state
