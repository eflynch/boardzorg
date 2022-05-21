from copy import deepcopy

from boardzorg.actions.action import Action
from boardzorg.actions import args
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.actions.author import discard_author
from boardzorg.actions.battle import ops


def get_loser(game_state):
    winner = game_state.round_state.stage_state.winner
    return [faction for faction in game_state.round_state.stage_state.battle[:2] if faction != winner][0]


def get_capturable_characters(game_state):
    winner = game_state.round_state.stage_state.winner
    if winner != "piglet":
        return []

    loser = get_loser(game_state)

    return list(filter(
        lambda character: character not in game_state.round_state.characters_used,
        game_state.faction_state[loser].characters))


class CharacterCapture(Action):
    name = "character-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "character-capture"
    ck_faction = "piglet"

    @classmethod
    def _check(cls, game_state, faction):
        if not get_capturable_characters(game_state):
            raise IllegalAction("There must be a capturable character")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        loser = get_loser(new_game_state)
        choice = new_game_state.random_choice_deck.pop(0)
        capturable_characters = get_capturable_characters(new_game_state)
        character_to_capture = capturable_characters[choice % len(capturable_characters)]
        new_game_state.faction_state[loser].characters.remove(character_to_capture)
        new_game_state.faction_state["piglet"].characters.append(character_to_capture)
        new_game_state.faction_state["piglet"].characters_captured.append(character_to_capture)
        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.stage = "main"
        return new_game_state


class CharacterCaptureLost(Action):
    name = "character-capture-lost"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "character-capture"
    ck_faction = "piglet"

    @classmethod
    def _check(cls, game_state, faction):
        if not get_capturable_characters(game_state):
            raise IllegalAction("There must be a capturable character")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        loser = get_loser(new_game_state)
        choice = new_game_state.random_choice_deck.pop(0)
        capturable_characters = get_capturable_characters(new_game_state)
        character_to_lost = capturable_characters[choice % len(capturable_characters)]
        ops.lost_character(new_game_state, loser, character_to_lost)
        game_state.faction_state["piglet"].hunny += 2
        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.stage = "main"
        return new_game_state


class PassCharacterCapture(Action):
    name = "pass-character-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "character-capture"
    ck_faction = "piglet"

    @classmethod
    def _check(cls, game_state, faction):
        if not get_capturable_characters(game_state):
            raise IllegalAction("There must be a capturable character")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.stage = "main"
        return new_game_state


class SkipCharacterCapture(Action):
    name = "skip-character-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "character-capture"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if get_capturable_characters(game_state):
            raise IllegalAction("Piglet can capture a character")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.stage = "main"
        return new_game_state


class AuthorCharacterCapture(Action):
    name = "author-character-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-character-capture"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.stage_state.author_character_capture_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.stage = "main"
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassCharacterCapture(Action):
    name = "author-pass-character-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-character-capture"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "piglet":
            raise IllegalAction("You cannot karam your own character capture!")
        if faction in game_state.round_state.stage_state.author_character_capture_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_character_capture_passes.append(self.faction)
        return new_game_state


class SkipAuthorCharacterCapture(Action):
    name = "skip-author-character-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "author-character-capture"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if get_capturable_characters(game_state):
            if len(game_state.round_state.stage_state.author_character_capture_passes) != len(game_state.faction_state) - 1:
                raise IllegalAction("Still waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "character-capture"
        return new_game_state
