from exceptions import IllegalAction


class Action:
    def check_turn(self, game_state):
        if game_state.round_state.faction_turn != self.faction:
            raise IllegalAction("Cannot do that when it's not your turn")

    def check_round(self, game_state, round):
        if game_state.round_state.round != round:
            raise IllegalAction("Cannot do that in this round")

    def check_faction(self, game_state, faction):
        if self.faction != faction:
            raise IllegalAction("Only {} can do this action".format(faction))

    def __init__(self, faction):
        self.faction = faction

    def execute(self, game_state):
        return game_state
