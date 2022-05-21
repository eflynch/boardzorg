from copy import deepcopy
from logging import getLogger

from boardzorg.actions.action import Action
from boardzorg.actions import args
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.actions.author import discard_author

logger = getLogger(__name__)


class Cleverness(Action):
    name = "cleverness"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "cleverness"
    ck_faction = "rabbit"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 2:
            no, cleverness = parts
            if no != "no":
                raise BadCommand("No means no")
            no = True
        elif len(parts) == 1:
            cleverness = parts[0]
            no = False
        else:
            raise BadCommand("Bad args")

        if (cleverness not in [f"{flavor}-{category}"
                          for flavor in ["projectile", "bee_trouble"]
                          for category in ["weapon", "defense"]]) and (
            cleverness not in ("anti_umbrella", "worthless", "cheap-hero-heroine")):
            raise BadCommand("Not something you can cleverness!")

        return Cleverness(faction, no, cleverness)

    @classmethod
    def get_arg_spec(clas, faction=None, game_state=None):
        return args.Cleverness()

    @classmethod
    def _check(cls, game_state, faction):
        if "rabbit" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["rabbit"]:
                if defender not in game_state.alliances["rabbit"]:
                    raise IllegalAction("No legal cleverness is possible")

    def __init__(self, faction, no, cleverness):
        self.faction = faction
        self.no = no
        self.cleverness = cleverness

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        if self.faction == battle_id[0] or self.faction in new_game_state.alliances[battle_id[0]]:
            new_game_state.round_state.stage_state.cleverness_is_attacker = False
        elif self.faction == battle_id[1] or self.faction in new_game_state.alliances[battle_id[1]]:
            new_game_state.round_state.stage_state.cleverness_is_attacker = True
        else:
            raise BadCommand("You ain't voicing no one")

        new_game_state.round_state.stage_state.cleverness = (self.no, self.cleverness)
        new_game_state.round_state.stage_state.substage = "author-cleverness"
        return new_game_state


class PassCleverness(Action):
    name = "pass-cleverness"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "cleverness"
    ck_faction = "rabbit"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-very_sad_boys"
        return new_game_state


class SkipCleverness(Action):
    name = "skip-cleverness"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "cleverness"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "rabbit" in game_state.faction_state:
            if "rabbit" in game_state.round_state.stage_state.battle:
                raise IllegalAction("The rabbit may use the cleverness")
            if "rabbit" in game_state.alliances[game_state.round_state.stage_state.battle[0]]:
                raise IllegalAction("The rabbit may use the cleverness on behalf of their attacker ally")
            if "rabbit" in game_state.alliances[game_state.round_state.stage_state.battle[1]]:
                raise IllegalAction("The rabbit may use the cleverness on behalf of their defender ally")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-very_sad_boys"
        return new_game_state


class AuthorCleverness(Action):
    name = "author-cleverness"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-cleverness"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.stage_state.cleverness_author_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.cleverness_is_attacker = False
        new_game_state.round_state.stage_state.cleverness = None
        new_game_state.round_state.stage_state.substage = "author-very_sad_boys"
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassCleverness(Action):
    name = "author-pass-cleverness"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-cleverness"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "rabbit":
            raise IllegalAction("You cannot karam your own cleverness!")
        if faction in game_state.round_state.stage_state.cleverness_author_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.cleverness_author_passes.append(self.faction)
        return new_game_state


class SkipAuthorCleverness(Action):
    name = "skip-author-cleverness"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-cleverness"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.cleverness_author_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Still waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-very_sad_boys"
        return new_game_state
