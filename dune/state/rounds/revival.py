from dune.state.rounds import RoundState


class RevivalRound(RoundState):
    def __init__(self):
        self.round = "revival"
        self.faction_turn = None

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["faction_turn"] = self.faction_turn

        return visible
