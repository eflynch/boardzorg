from boardzorg.state.rounds import RoundState


class RetrievalRound(RoundState):
    round = "retrieval"

    def __init__(self):
        self.stage = "main"
        self.faction_turn = None
        self.factions_done = []
        self.christopher_robbin_blessings = []
        self.eeyore_ally_retrieval_done = False

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["faction_turn"] = self.faction_turn
        visible["factions_done"] = self.factions_done

        return visible
