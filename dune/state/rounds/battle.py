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
#   karama-sardaukar : KARama / pass / skip
#   karama-fedykin : karama / pass / skip
#   prescience : Prescience / Pass / Skip
#   karama-prescience : KARAMA_CAncel_Presecience / Answer Prescience question
#   karama-entire : KARMA_Entire Battle plan / Pass / skip
#   reveal-entire : Reveal entire plan
#   karama-kwisatz-harderach : KARAMA_cancel_kh / pass / skip
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

        self.reveal_entire = None
        self.reveal_entire_is_attacker = False

        self.voice_karama_passes = []

        self.karama_sardaukar = False
        self.karama_sardaukar_passes = []

        self.karama_fedaykin = False
        self.karama_fedaykin_passes = []

        self.karama_kwisatz_haderach = False
        self.karama_kwisatz_haderach_passes = []

        self.karama_leader_capture_passes = []

        self.traitor_passes = []
        self.traitor_revealers = []

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["battle"] = self.battle
        visible["winner"] = self.winner
        visible["prescience"] = self.prescience
        visible["prescience_is_attacker"] = self.prescience_is_attacker
        visible["reveal_entire"] = self.reveal_entire
        visible["reveal_entire_is_attacker"] = self.reveal_entire_is_attacker
        visible["substage"] = self.substage
        visible["voice"] = self.voice
        visible["voice_is_attacker"] = self.voice_is_attacker
        visible["karama_sardaukar"] = self.karama_sardaukar
        visible["karama_fedaykin"] = self.karama_fedaykin
        visible["karama_kwisatz_haderach"] = self.karama_kwisatz_haderach
        visible["traitor_revealers"] = self.traitor_revealers

        attacker = None
        defender = None
        if self.battle is not None:
            attacker = self.battle[0]
            defender = self.battle[1]

        stage_allows = self.substage in ["traitors", "resolve", "winner"]

        reveal_entire_attack = attacker == faction or (self.reveal_entire and self.reveal_entire_is_attacker) or stage_allows 
        reveal_entire_defense = defender == faction or (self.reveal_entire and not self.reveal_entire_is_attacker) or stage_allows 

        if reveal_entire_attack:
            visible["attacker_plan"] = self.attacker_plan
        if reveal_entire_defense:
            visible["defender_plan"] = self.defender_plan

        if self.prescience is not None:
            relevant_plan = self.attacker_plan if self.prescience_is_attacker else self.defender_plan
            relevant_plan_key = "attacker_plan" if self.prescience_is_attacker else "defender_plan"
            if self.prescience in relevant_plan:
                if relevant_plan_key not in visible:
                    visible[relevant_plan_key] = {self.prescience: relevant_plan[self.prescience]}

        return visible


class BattleRound(RoundState):
    round = "battle"

    def __init__(self):
        self.faction_turn = None
        self.leaders_used = {}

        self.kwisatz_haderach_leader = None
        self.kwisatz_haderach_leader_revealed = False

        self.battles = None
        self.stage = "setup"

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["faction_turn"] = self.faction_turn
        visible["battles"] = self.battles
        visible["leaders_used"] = self.leaders_used
        visible["stage"] = self.stage
        if self.stage == "battle":
            visible["stage_state"] = self.stage_state.visible(game_state, faction)
        if self.kwisatz_haderach_leader_revealed or faction == "atreides":
            visible["kwisatz_haderach_leader"] = self.kwisatz_haderach_leader
        return visible
