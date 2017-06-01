from dune.state.rounds import RoundState


class MovementRound(RoundState):
    def __init__(self):
        self.round = "movement"
        self.faction_turn = None
        self.block_guild_turn_karama_used = False
        self.block_guild_turn_karama_pass = []
