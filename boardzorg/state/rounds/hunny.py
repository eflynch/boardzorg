from boardzorg.state.rounds import RoundState, StageState, SubStageState


class HandleHeffalumpForces(SubStageState):
    substage = "forces"

    def __init__(self):
        self.author_passes = []


class ResolveHeffalumpStage(StageState):
    stage = "heffalump"

    def __init__(self, factions):
        self.factions = factions
        self.faction_turn = None

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["factions"] = self.factions
        visible["faction_turn"] = self.faction_turn
        return visible


class HunnyRound(RoundState):
    round = "hunny"

    def __init__(self):
        self.stage = "christopher_robbin-heffalump-author"
        self.drawn_card = False
        self.needs_picnick = False
        self.christopher_robbin_can_redirect_heffalump = False

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["stage_state"] = self.stage_state.visible(game_state, faction) if self.stage_state else None
        return visible