from dune.state.rounds import RoundState


class NexusRound(RoundState):
    def __init__(self):
        self.round = "nexus"
        self.proposals = {}
        self.proposals_done = False
        self.worm_done = False
        self.karama_done = False
        self.karama_passes = []
        self.shai_hulud = None
