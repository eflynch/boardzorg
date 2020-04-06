from copy import deepcopy
from logging import getLogger

from dune.actions import args
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.actions.battle import ops
from dune.actions.karama import discard_karama

logger = getLogger(__name__)


class Prescience(Action):
    name = "prescience"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "prescience"
    ck_faction = "atreides"

    @classmethod
    def parse_args(cls, faction, args):
        part = args
        if part not in ["leader", "number", "weapon", "defense"]:
            raise BadCommand("Not a valid prescience question")
        return Prescience(faction, part)

    def __init__(self, faction, part):
        self.faction = faction
        self.part = part

    @classmethod
    def get_arg_spec(cls, faction=None):
        return args.String();

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        if self.faction == battle_id[0] or self.faction in new_game_state.alliances[battle_id[0]]:
            new_game_state.round_state.stage_state.prescience_is_attacker = False
        elif self.faction == battle_id[1] or self.faction in new_game_state.alliances[battle_id[1]]:
            new_game_state.round_state.stage_state.prescience_is_attacker = True
        else:
            raise BadCommand("You can't do that")
        new_game_state.round_state.stage_state.prescience = self.part
        new_game_state.round_state.stage_state.substage = "karama-prescience"
        return new_game_state


class PresciencePass(Action):
    name = "prescience-pass"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "prescience"
    ck_faction = "atreides"

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-entire"
        return new_game_state


class PrescienceSkip(Action):
    name = "prescience-skip"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "prescience"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" in game_state.faction_state:
            if "atreides" in game_state.round_state.stage_state.battle:
                raise IllegalAction("Cannot skip since atreides are in the battle")
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")
            if defender in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-entire"
        return new_game_state


class AnswerPrescience(Action):
    name = "answer-prescience"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-prescience"

    @classmethod
    def parse_args(cls, faction, args):
        part = args
        return AnswerPrescience(faction, part)

    @classmethod
    def get_arg_spec(cls, faction=None):
        return args.String();


    def __init__(self, faction, part):
        self.faction = faction
        self.part = part

    @classmethod
    def _check(cls, game_state, faction):
        battle_id = game_state.round_state.stage_state.battle
        if game_state.round_state.stage_state.prescience is not None:
            if game_state.round_state.stage_state.prescience_is_attacker:
                if faction != battle_id[0]:
                    raise IllegalAction("Only the embattled can define the future")
            else:
                if faction != battle_id[1]:
                    raise IllegalAction("Only the embattled can define the future")
        else:
            raise IllegalAction("No prescience to answer")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        prescience = new_game_state.round_state.stage_state.prescience
        is_attacker = new_game_state.round_state.stage_state.prescience_is_attacker

        if prescience == "leader":
            ops.pick_leader(new_game_state, is_attacker, self.part)
        elif prescience == "number":
            ops.pick_number(new_game_state, is_attacker, int(self.part))
        elif prescience == "weapon":
            ops.pick_weapon(new_game_state, is_attacker, self.part if self.part != "-" else None)
        elif prescience == "defense":
            ops.pick_defense(new_game_state, is_attacker, self.part if self.part != "-" else None)
        else:
            raise BadCommand("Something bad happened")

        new_game_state.round_state.stage_state.substage = "karama-entire"
        return new_game_state


class KaramaPrescience(Action):
    name = "karama-prescience"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-prescience"
    ck_karama = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.prescience = None
        new_game_state.round_state.stage_state.prescience_is_attacker = False
        new_game_state.round_state.stage_state.substage = "karama-entire"
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaEntirePlan(Action):
    name = "karama-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-entire"
    ck_faction = "atreides"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "reveal-entire"
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaPassEntirePlan(Action):
    name = "karama-pass-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-entire"
    ck_faction = "atreides"

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-kwizatz-haderach"
        return new_game_state


class SkipKaramaEntirePlan(Action):
    name = "skip-karama-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-entire"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" in game_state.faction_state:
            if "atreides" in game_state.round_state.stage_state.battle:
                raise IllegalAction("Cannot skip since atreides are in the battle")
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")
            if defender in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-kwizatz-haderach"
        return new_game_state
