from dune.state.rounds import RoundState, StageState, SubStageState


class HandleWormForces(SubStageState):
    substage = "forces"

    def __init__(self):
        self.karama_passes = []


class ResolveWormStage(StageState):
    stage = "worm"

    def __init__(self, factions):
        self.factions = factions
        self.faction_turn = None

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["factions"] = self.factions
        visible["faction_turn"] = self.faction_turn
        return visible


class SpiceRound(RoundState):
    round = "spice"

    def __init__(self):
        self.stage = "fremen-worm-karama"
        self.drawn_card = False
        self.needs_nexus = False

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["stage_state"] = self.stage_state.visible(game_state, faction) if self.stage_state else None
        return visible