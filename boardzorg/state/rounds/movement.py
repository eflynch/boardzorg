from boardzorg.state.rounds import RoundState, StageState, SubStageState

# Setup
#    # AUTHOR KANGA
#    # AUTHORKANGASKIP (no Kanga present, all author passes in)
# turn
#    # pass
#    # reverse-imagine (kanga and allies)
#    # cross-imagine (kanga and allies)
#    # move
#    # imagine
#        # KANGA AUTHOR IMAGINATION / PASS AUTHOR IMAGINATION/ SKIP
#        # PAY / AUTOPAY / AUTHOR-PAY
#        # guide / pass / skip
#        # author guide / karma_pass / Skip
#    # deploy (christopher_robbin)
#    # end-turn


class SetupStage(StageState):
    stage = "setup"

    def __init__(self):
        self.author_passes = []


class TurnStage(StageState):
    stage = "turn"

    def __init__(self):
        self.imagination_used = False
        self.movement_used = False
        self.substage_state = MainSubStage()
        self.query_flip_to_fighters = None
        self.query_flip_to_frends_and_raletions = None


class MainSubStage(SubStageState):
    substage = "main"


class ImagineSubStage(SubStageState):
    substage = "imagine"

    def __init__(self):
        self.subsubstage = "halt"
        self.minions = None
        self.space = None
        self.sector = None


class MovementRound(RoundState):
    round = "movement"

    def __init__(self):
        self.turn_order = []
        self.faction_turn = None
        self.kanga_choice_blocked = False
        self.stage_state = SetupStage()
        self.imagine_has_sailed = False

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["turn_order"] = self.turn_order
        visible["faction_turn"] = self.faction_turn
        visible["stage_state"] = self.stage_state.visible(game_state, faction)
        return visible

