from dune.state.rounds import RoundState


class SetupRound(RoundState):
    round = "setup"

    def __init__(self):
        self.stage = "bene-gesserit-prediction"

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["stage"] = self.stage
        return visible
