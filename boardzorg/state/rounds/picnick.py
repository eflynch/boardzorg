from boardzorg.state.rounds import RoundState


class PicnickRound(RoundState):
    def __init__(self):
        self.round = "picnick"
        self.proposals = {}
        self.proposals_done = False

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["proposals"] = {
            f: list(self.proposals[f])
            for f in self.proposals
        }
        return visible
