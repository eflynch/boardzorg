from boardzorg.state.rounds import RoundState, StageState, SubStageState

# a) Issue the Cleverness command,
# b) Play Author to cancel the Cleverness.
# c) Issue the Flight question,
# d) Play Author to cancel the Flight.
# e) Answer the Flight question (if not canceled).
# f) Play Author to view entire battle plan.
# g) Play Author to cancel Kwisatz Haderach.
# h) Play Author to cancel VerySadBoys or Woozles bonus.
# i) Commit battle plans.
# j) Reveal battle plans.
# Block H Character Capture
# k) Resolve the battle.

# setup
# main: pick battle / auto-pick-battle
# battle :
#   cleverness : Cleverness / Cleverness Pass / Cleverness Skip
#   karam-cleverness : AUTHOR_Cancel_Cleverness / pass
#   author-very_sad_boys : KARama / pass / skip
#   author-fedykin : author / pass / skip
#   flight : Flight / Pass / Skip
#   author-flight : AUTHOR_CAncel_Presecience / Answer Flight question
#   author-entire : KARMA_Entire Battle plan / Pass / skip
#   reveal-entire : Reveal entire plan
#   author-kwisatz-harderach : AUTHOR_cancel_kh / pass / skip
#   commit-battle-plans : commit-plan / auto-commit-plan
#   traitors : reveal-traitor / pass-reveal-traitor / skip
#   resolve-battle : auto-resolve
#   winner-actions : lost-minions / discard / done

#  TODO:
#   author-captured-character : author / pass / skip
#   capture-character : capture-character / pass
#   lost-character : lost-character / keep-character


class WinnerSubStage(SubStageState):
    substage = "winner"

    def __init__(self):
        self.power_left_to_lost = None
        self.discard_done = False


class BattleStage(StageState):
    stage = "battle"

    def __init__(self):
        self.battle = None
        self.winner = None
        self.substage = "cleverness"
        self.attacker_plan = {}
        self.defender_plan = {}

        self.cleverness = None
        self.cleverness_is_attacker = False

        self.flight = None
        self.flight_is_attacker = False

        self.reveal_entire = None
        self.reveal_entire_is_attacker = False

        self.cleverness_author_passes = []
        self.flight_author_passes = []

        self.author_very_sad_boys = False
        self.author_very_sad_boys_passes = []

        self.author_woozles = False
        self.author_woozles_passes = []

        self.author_winnie_the_pooh = False
        self.author_winnie_the_pooh_passes = []

        self.author_character_capture_passes = []

        self.traitor_passes = []
        self.traitor_revealers = []

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["battle"] = self.battle
        visible["winner"] = self.winner
        visible["flight"] = self.flight
        visible["flight_is_attacker"] = self.flight_is_attacker
        visible["reveal_entire"] = self.reveal_entire
        visible["reveal_entire_is_attacker"] = self.reveal_entire_is_attacker
        visible["substage"] = self.substage
        visible["cleverness"] = self.cleverness
        visible["cleverness_is_attacker"] = self.cleverness_is_attacker
        visible["author_very_sad_boys"] = self.author_very_sad_boys
        visible["author_woozles"] = self.author_woozles
        visible["author_winnie_the_pooh"] = self.author_winnie_the_pooh
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

        if self.flight is not None:
            relevant_plan = self.attacker_plan if self.flight_is_attacker else self.defender_plan
            relevant_plan_key = "attacker_plan" if self.flight_is_attacker else "defender_plan"
            if self.flight in relevant_plan:
                if relevant_plan_key not in visible:
                    visible[relevant_plan_key] = {self.flight: relevant_plan[self.flight]}

        return visible


class BattleRound(RoundState):
    round = "battle"

    def __init__(self):
        self.faction_turn = None
        self.characters_used = {}

        self.winnie_the_pooh_character = None
        self.winnie_the_pooh_character_revealed = False

        self.battles = None
        self.stage = "setup"

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["faction_turn"] = self.faction_turn
        visible["battles"] = self.battles
        visible["characters_used"] = self.characters_used
        visible["stage"] = self.stage
        if self.stage == "battle":
            visible["stage_state"] = self.stage_state.visible(game_state, faction)
        if self.winnie_the_pooh_character_revealed or faction == "owl":
            visible["winnie_the_pooh_character"] = self.winnie_the_pooh_character
        return visible
