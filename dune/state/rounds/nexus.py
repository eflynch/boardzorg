from dune.state.rounds import RoundState


class NexusRound(RoundState):
    def __init__(self):
        self.round = "nexus"
        self.proposals = {}
        self.proposals_done = False
        self.worm_done = False
        self.karama_done = False
        self.karama_passes = []

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["proposals"] = {
            f: list(self.proposals[f])
            for f in self.proposals
        }
        return visible
