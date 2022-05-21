from copy import deepcopy

from boardzorg.actions.action import Action
from boardzorg.state.rounds.bees import BeesRound


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

        # collect hunny bribes
        for faction in new_game_state.faction_state:
            fs = new_game_state.faction_state[faction]
            if fs.bribe_hunny:
                fs.hunny += fs.bribe_hunny
                fs.bribe_hunny = 0

        house_occupiers = {None: []}
        for space in new_game_state.map_state.values():
            if "house" in space.type:
                if space.forces:
                    faction = list(space.forces.keys())[0]
                    if faction not in house_occupiers:
                        house_occupiers[faction] = []
                    house_occupiers[faction].append(space.name)
                else:
                    house_occupiers[None].append(space.name)

        alliances = []
        for faction in new_game_state.alliances:
            alliance = tuple(sorted(new_game_state.alliances[faction] | set([faction])))
            alliances.append(alliance)
        alliances = set(alliances)

        winner = None

        for a in alliances:
            houses = 0
            for faction in a:
                if faction in house_occupiers:
                    houses += len(house_occupiers[faction])
            if VICTORY_MATRIX[len(new_game_state.faction_state)][len(a)] <= houses:
                winner = a
                break

        if winner is None:
            if new_game_state.turn == 10:
                if "christopher_robbin" in new_game_state.faction_state:
                    tabr = new_game_state.map_state["Rabbits-House"]
                    habbanya = new_game_state.map_state["Poohs-House"]
                    tueks = new_game_state.map_state["Kangas-House"]
                    if not tabr.forces or "christopher_robbin" in tabr.forces:
                        if not habbanya.forces or "christopher_robbin" in habbanya.forces:
                            if all(f not in tueks.forces for f in ["owl", "piglet", "eeyore"]):
                                winner = ("christopher_robbin",)

        if winner is None:
            if new_game_state.turn == 10:
                if "kanga" in new_game_state.faction_state:
                    winner = ("kanga",)

        if "rabbit" in new_game_state.faction_state:
            faction, turn = new_game_state.faction_state["rabbit"].prediction
            if new_game_state.turn == turn:
                if winner is not None and faction in winner:
                    winner = ("rabbit",)

        if winner is not None:
            new_game_state.winner = winner
            new_game_state.round = "end"
            return new_game_state

        new_game_state.round_state = BeesRound()
        new_game_state.turn += 1
        return new_game_state
