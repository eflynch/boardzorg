from boardzorg.state.rounds import RoundState, StageState, SubStageState

# Setup
#    # KARAMA GUILD
#    # KARAMAGUILDSKIP (no Guild present, all karama passes in)
# turn
#    # pass
#    # reverse-ship (guild and allies)
#    # cross-ship (guild and allies)
#    # move
#    # ship
#        # GUILD KARAMA SHIPMENT / PASS KARAMA SHIPMENT/ SKIP
#        # PAY / AUTOPAY / KARAMA-PAY
#        # guide / pass / skip
#        # karama guide / karma_pass / Skip
#    # deploy (fremen)
#    # end-turn


class SetupStage(StageState):
    stage = "setup"

    def __init__(self):
        self.karama_passes = []


class TurnStage(StageState):
    stage = "turn"

    def __init__(self):
        self.shipment_used = False
        self.movement_used = False
        self.substage_state = MainSubStage()
        self.query_flip_to_fighters = None
        self.query_flip_to_advisors = None


class MainSubStage(SubStageState):
    substage = "main"


class ShipSubStage(SubStageState):
    substage = "ship"

    def __init__(self):
        self.subsubstage = "halt"
        self.units = None
        self.space = None
        self.sector = None


class MovementRound(RoundState):
    round = "movement"

    def __init__(self):
        self.turn_order = []
        self.faction_turn = None
        self.guild_choice_blocked = False
        self.stage_state = SetupStage()
        self.ship_has_sailed = False

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["turn_order"] = self.turn_order
        visible["faction_turn"] = self.faction_turn
        visible["stage_state"] = self.stage_state.visible(game_state, faction)
        return visible

