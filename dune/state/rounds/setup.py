from dune.state.rounds import RoundState


class SetupRound(RoundState):
    def __init__(self):
        self.round = "setup"
