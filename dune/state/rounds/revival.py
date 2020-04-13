from dune.state.rounds import RoundState


class RevivalRound(RoundState):
    round = "revival"

    def __init__(self):
        self.stage = "main"
        self.faction_turn = None
        self.factions_done = []

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["faction_turn"] = self.faction_turn
        visible["factions_done"] = self.factions_done

        return visible
