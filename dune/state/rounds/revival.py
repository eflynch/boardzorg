from dune.state.rounds import RoundState


class RevivalRound(RoundState):
    round = "revival"

    def __init__(self):
        self.stage = "main"
        self.faction_turn = None
        self.factions_done = []
        self.fremen_blessings = []
        self.emperor_ally_revival_done = False

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["faction_turn"] = self.faction_turn
        visible["factions_done"] = self.factions_done

        return visible
