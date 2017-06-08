from dune.state.rounds import RoundState, StageState, SubStageState

# Setup
#    # KARAMA GUILD
#    # KARAMAGUILDSKIP (no Guild present, all karama passes in)
# Coexist
#    # COEXIST PLACE
#    # COEXIST PERSIST
#    # COEXISTSKIP (no bg Present)
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


class CoexistStage(StageState):
    stage = "coexist"


class TurnStage(StageState):
    stage = "turn"

    def __init__(self):
        self.shipment_used = False
        self.movement_used = False
        self.substage_state = MainSubStage()


class MainSubStage(SubStageState):
    substage = "main"


class ShipSubStage(SubStageState):
    substage = "ship"

    def __init__(self):
        self.subsubstage = "halt"
        self.units = None
        self.space = None
        self.sector = None
        self.coexist = None


class MovementRound(RoundState):
    round = "movement"

    def __init__(self):
        self.turn_order = []
        self.faction_turn = None
        self.guild_choice_blocked = False
        self.stage_state = SetupStage()
