from dune.state.rounds import RoundState, StageState, SubStageState

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
#   karama-entire : KARMA_Entire Battle plan / Pass / skip
#   reveal-entire : Reveal entire plan
#   karama-kwizatz-harderach : KARAMA_cancel_kh / pass / skip
#   karama-sardaukar : KARama / pass / skip
#   karama-fedykin : karama / pass / skip
#   commit-battle-plans : commit-plan / auto-commit-plan
#   traitors : reveal-traitor / pass-reveal-traitor / skip
#   resolve-battle : auto-resolve
#   winner-actions : tank-units / discard / done

#  TODO:
#   karama-captured-leader : karama / pass / skip
#   capture-leader : capture-leader / pass
#   tank-leader : tank-leader / keep-leader


class WinnerSubStage(SubStageState):
    substage = "winner"

    def __init__(self):
        self.power_left_to_tank = None
        self.discard_done = False


class BattleStage(StageState):
    stage = "battle"

    def __init__(self):
        self.battle = None
        self.winner = None
        self.substage = "voice"
        self.attacker_plan = {}
        self.defender_plan = {}

        self.voice = None
        self.voice_is_attacker = False

        self.prescience = None
        self.prescience_is_attacker = False

        self.voice_karama_passes = []

        self.karama_sardaukar = False
        self.karama_sardaukar_passes = []

        self.karama_fedaykin = False
        self.karama_fedaykin_passes = []

        self.karama_kwizatz_haderach = False
        self.karama_kwizatz_haderach_passes = []

        self.traitor_passes = []


class BattleRound(RoundState):
    round = "battle"

    def __init__(self):
        self.faction_turn = None
        self.faction_order = None
        self.leaders_used = {}
        self.battles = None
        self.stage = "setup"
