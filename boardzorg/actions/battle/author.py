from copy import deepcopy
from logging import getLogger

from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction
from boardzorg.actions.author import discard_author

logger = getLogger(__name__)


class AuthorWinnieThePooh(Action):
    name = "author-winnie-the-pooh"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-winnie-the-pooh"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "owl":
            raise IllegalAction("You cannot author your own messiah")
        if "owl" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No Kwisatz to Haderach")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_winnie_the_pooh = True
        new_game_state.round_state.stage_state.substage = "finalize"
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassWinnieThePooh(Action):
    name = "author-pass-winnie-the-pooh"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-winnie-the-pooh"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "owl":
            raise IllegalAction("You cannot author your own messiah")
        if "owl" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No Kwisatz to Haderach")
        if faction in game_state.round_state.stage_state.author_winnie_the_pooh_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_winnie_the_pooh_passes.append(self.faction)
        return new_game_state


class SkipAuthorWinnieThePooh(Action):
    name = "skip-author-winnie-the-pooh"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-winnie-the-pooh"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "owl" in game_state.faction_state:
            if "owl" in game_state.round_state.stage_state.battle:
                passes = len(game_state.round_state.stage_state.author_winnie_the_pooh_passes)
                if passes != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "finalize"
        return new_game_state


class AuthorVerySadBoys(Action):
    name = "author-very_sad_boys"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-very_sad_boys"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "eeyore":
            raise IllegalAction("You cannot author your own slave soldier things")
        if "eeyore" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No sar to kar")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_very_sad_boys = True
        new_game_state.round_state.stage_state.substage = "author-woozles"
        discard_karma(new_game_state, self.faction)
        return new_game_state


class AuthorPassVerySadBoys(Action):
    name = "author-pass-very_sad_boys"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-very_sad_boys"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "eeyore":
            raise IllegalAction("You cannot author your own slave soldier things")
        if "eeyore" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No sar to kar")
        if faction in game_state.round_state.stage_state.author_very_sad_boys_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_very_sad_boys_passes.append(self.faction)
        return new_game_state


class SkipAuthorVerySadBoys(Action):
    name = "skip-author-very_sad_boys"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-very_sad_boys"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "eeyore" in game_state.faction_state:
            if "eeyore" in game_state.round_state.stage_state.battle:
                if len(game_state.round_state.stage_state.author_very_sad_boys_passes) != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "author-woozles"
        return new_game_state


class AuthorWoozles(Action):
    name = "author-woozles"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-woozles"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "christopher_robbin":
            raise IllegalAction("You cannot author your own man dudes")
        if "christopher_robbin" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No woozles")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_woozles = True
        new_game_state.round_state.stage_state.substage = "flight"
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassWoozles(Action):
    name = "author-pass-woozles"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-woozles"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "christopher_robbin":
            raise IllegalAction("You cannot author your own main dudes")
        if "christopher_robbin" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("no woozles")
        if faction in game_state.round_state.stage_state.author_woozles_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_woozles_passes.append(self.faction)
        return new_game_state


class SkipAuthorWoozles(Action):
    name = "skip-author-woozles"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-woozles"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "christopher_robbin" in game_state.faction_state:
            if "christopher_robbin" in game_state.round_state.stage_state.battle:
                if len(game_state.round_state.stage_state.author_woozles_passes) != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "flight"
        return new_game_state
