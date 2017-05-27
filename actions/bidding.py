from copy import deepcopy

from exceptions import IllegalAction

from actions.action import Action


class ChoamCharity(Action):
    def parse_args(faction, args):
        return ChoamCharity(faction)

    def __init__(self, faction):
        self.faction = faction

    def execute(self, game_state):
        self.check_round(game_state, "bidding")
        new_game_state = deepcopy(game_state)

        if self.faction != "bene-gesserit" and new_game_state.faction_state[self.faction].spice > 0:
            raise IllegalAction("CHOAM Charity is only for the poor and meek")

        if self.faction == "bene-gesserit" and new_game_state.round_state.bene_gesserit_charity_claimed:
            raise IllegalAction("CHOAM is generous but not so generous")

        new_game_state.faction_state[self.faction].spice += 2
        if self.faction == "bene-gesserit":
            new_game_state.round_state.bene_gesserit_charity_claimed = True

        return new_game_state
