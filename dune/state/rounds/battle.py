from dune.state.rounds import RoundState


class BattleRound(RoundState):
    def __init__(self):
        self.round = "battle"
        self.faction_turn = "atreides"
