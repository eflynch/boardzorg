from dune.state.rounds import RoundState, StageState

# a) Issue the Voice command,
# b) Play Karama to cancel the Voice.
# c) Issue the Prescience question,
# d) Play Karama to cancel the Prescience.
# e) Answer the Prescience question (if not canceled).
# f) Play Karama to view entire battle plan.
# g) Play Karama to cancel Kwisatz Haderach.
# h) Play Karama to cancel Sardaukar or Fedaykin bonus.
# i) Commit battle plans.
# j) Reveal battle plans.
# Block H Leader Capture
# k) Resolve the battle.

# setup
# main: pick battle / auto-pick-battle
# battle :
#   voice : Voice / Voice Pass / Voice Skip
#   karam-voice : KARAMA_Cancel_Voice / pass
#   prescience : Prescience / Pass / Skip
#   karama-prescience : KARAMA_CAncel_Presecience / Answer Prescience question
#   karama-entire : KARMA_Entire Battle plan / Pass
#   reveal-entire : Reveal entire plan
#   karama-kwizatz-harderach : KARAMA_cancel_kh / pass / skip
#   karama-sardaukar : KARama / pass / skip
#   karama-fedykin : karama / pass / skip
#   commit-battle-plans : commit-plan / auto-commit-plan
#   traitors : reveal-traitor / pass-reveal-traitor / skip
#   resolve-battle : auto-resolve / tank-units
#   karama-captured-leader : karama / pass / skip
#   capture-leader : capture-leader / pass


class BattleStage(StageState):
    stage = "battle"

    def __init__(self):
        self.attacker = None
        self.defender = None
        self.space = None
        self.substage = "voice"
        self.attacker_plan = {}
        self.defender_plan = {}

        self.attacker_voiced = None
        self.defender_voiced = None

        self.attacker_prescience = None
        self.defender_prescience = None

        self.karama_sardaukar = False
        self.karama_fedaykin = False
        self.karma_kwizatz_haderach = False


class MainStage(StageState):
    stage = "main"


class SetupStage(StageState):
    stage = "setup"


class BattleRound(RoundState):
    round = "battle"

    def __init__(self):
        self.faction_turn = None
        self.faction_order = None
        self.leaders_used = []
        self.battles = None
        self.stage_state = SetupStage()
