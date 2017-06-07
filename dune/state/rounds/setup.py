from dune.state.rounds import RoundState, StageState


class BeneGesseritPredictionStage(StageState):
    stage = "bene-gesserit-prediction"


class TokenPlacementStage(StageState):
    stage = "token-placement"


class TraitorStage(StageState):
    stage = "traitor"


class FremenPlacementStage(StageState):
    stage = "fremen-placement"


class BeneGesseritPlacementStage(StageState):
    stage = "bene-gesserit-placement"


class StormPlacementStage(StageState):
    stage = "storm-placement"


class SetupRound(RoundState):
    def __init__(self):
        self.round = "setup"
        self.stage_state = BeneGesseritPredictionStage()

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["stage"] = self.stage_state.stage
