from dune.state.rounds import RoundState


class RevivalRound(RoundState):
    def __init__(self):
        self.round = "revival"
        self.faction_turn = None
