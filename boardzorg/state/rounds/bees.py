from boardzorg.state.rounds import RoundState

class BeesRound(RoundState):
    round = "bees"

    def __init__(self):
        self.bee_keeping_passes = []
