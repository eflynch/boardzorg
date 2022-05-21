from copy import deepcopy
from logging import getLogger

from boardzorg.actions import args
from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.actions.battle import ops
from boardzorg.actions.author import discard_author

logger = getLogger(__name__)


class Flight(Action):
    name = "flight"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "flight"
    ck_faction = "owl"

    @classmethod
    def parse_args(cls, faction, args):
        part = args
        if part not in ["character", "number", "weapon", "defense"]:
            raise BadCommand("Not a valid flight question")
        return Flight(faction, part)

    def __init__(self, faction, part):
        self.faction = faction
        self.part = part

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Flight();

    @classmethod
    def _check(cls, game_state, faction):
        if "owl" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["owl"]:
                if defender not in game_state.alliances["owl"]:
                    raise IllegalAction("No legal flight is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        if self.faction == battle_id[0] or self.faction in new_game_state.alliances[battle_id[0]]:
            new_game_state.round_state.stage_state.flight_is_attacker = False
        elif self.faction == battle_id[1] or self.faction in new_game_state.alliances[battle_id[1]]:
            new_game_state.round_state.stage_state.flight_is_attacker = True
        else:
            raise BadCommand("You can't do that")
        new_game_state.round_state.stage_state.flight = self.part
        new_game_state.round_state.stage_state.substage = "author-flight"
        return new_game_state


class FlightPass(Action):
    name = "flight-pass"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "flight"
    ck_faction = "owl"

    @classmethod
    def _check(cls, game_state, faction):
        if "owl" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["owl"]:
                if defender not in game_state.alliances["owl"]:
                    raise IllegalAction("No legal flight is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-entire"
        return new_game_state


class FlightSkip(Action):
    name = "flight-skip"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "flight"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "owl" in game_state.faction_state:
            if "owl" in game_state.round_state.stage_state.battle:
                raise IllegalAction("Cannot skip since owl are in the battle")
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker in game_state.alliances["owl"]:
                raise IllegalAction("Cannot skip because allies of owl are in the battle")
            if defender in game_state.alliances["owl"]:
                raise IllegalAction("Cannot skip because allies of owl are in the battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-entire"
        return new_game_state


class AnswerFlight(Action):
    name = "answer-flight"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "answer-flight"

    @classmethod
    def parse_args(cls, faction, args):
        part = args
        return AnswerFlight(faction, part)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.FlightAnswer(max_power=ops.compute_max_power_faction(game_state, faction))

    def __init__(self, faction, part):
        self.faction = faction
        self.part = part if part != "-" else None

    @classmethod
    def _check(cls, game_state, faction):
        battle_id = game_state.round_state.stage_state.battle
        if game_state.round_state.stage_state.flight is not None:
            if game_state.round_state.stage_state.flight_is_attacker:
                if faction != battle_id[0]:
                    raise IllegalAction("Only the embattled can define the future")
            else:
                if faction != battle_id[1]:
                    raise IllegalAction("Only the embattled can define the future")
        else:
            raise IllegalAction("No flight to answer")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        flight = new_game_state.round_state.stage_state.flight
        is_attacker = new_game_state.round_state.stage_state.flight_is_attacker

        if flight == "character":
            ops.pick_character(new_game_state, is_attacker, self.part)
        elif flight == "number":
            try:
                number = int(self.part)
            except Exception as e:
                raise BadCommand("Not a good number")
            max_power = ops.compute_max_power_faction(game_state, self.faction)
            ops.pick_number(new_game_state, max_power, is_attacker, number)
        elif flight == "weapon":
            ops.pick_weapon(new_game_state, is_attacker, self.part if self.part != "-" else None)
        elif flight == "defense":
            ops.pick_defense(new_game_state, is_attacker, self.part if self.part != "-" else None)
        else:
            raise BadCommand("Something bad happened")

        new_game_state.round_state.stage_state.substage = "author-entire"
        return new_game_state


class AuthorFlight(Action):
    name = "author-flight"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-flight"
    ck_author = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.flight = None
        new_game_state.round_state.stage_state.flight_is_attacker = False
        new_game_state.round_state.stage_state.substage = "author-entire"
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassFlight(Action):
    name = "author-pass-flight"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-flight"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "owl":
            raise IllegalAction("You cannot karam your own flight")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.flight_author_passes.append(self.faction)
        return new_game_state


class SkipAuthorFlight(Action):
    name = "skip-author-flight"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-flight"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.flight_author_passes) < len(game_state.faction_state) - 1:
            raise IllegalAction("Waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "answer-flight"
        return new_game_state



class AuthorEntirePlan(Action):
    name = "author-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-entire"
    ck_faction_author = "owl"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if "owl" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["owl"]:
                if defender not in game_state.alliances["owl"]:
                    raise IllegalAction("No legal flight is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "reveal-entire"
        discard_author(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_author = True
        return new_game_state


class AuthorPassEntirePlan(Action):
    name = "author-pass-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-entire"
    ck_faction_author = "owl"

    @classmethod
    def _check(cls, game_state, faction):
        if "owl" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["owl"]:
                if defender not in game_state.alliances["owl"]:
                    raise IllegalAction("No legal flight is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-winnie-the-pooh"
        return new_game_state


class SkipAuthorEntirePlan(Action):
    name = "skip-author-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-entire"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "owl" in game_state.faction_state and not game_state.faction_state["owl"].used_faction_author:
            if "owl" in game_state.round_state.stage_state.battle:
                raise IllegalAction("Cannot skip since owl are in the battle")
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker in game_state.alliances["owl"]:
                raise IllegalAction("Cannot skip because allies of owl are in the battle")
            if defender in game_state.alliances["owl"]:
                raise IllegalAction("Cannot skip because allies of owl are in the battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-winnie-the-pooh"
        return new_game_state
