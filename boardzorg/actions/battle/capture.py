from copy import deepcopy

from boardzorg.actions.action import Action
from boardzorg.actions import args
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.actions.karama import discard_karama
from boardzorg.actions.battle import ops


def get_loser(game_state):
    winner = game_state.round_state.stage_state.winner
    return [faction for faction in game_state.round_state.stage_state.battle[:2] if faction != winner][0]


def get_capturable_leaders(game_state):
    winner = game_state.round_state.stage_state.winner
    if winner != "harkonnen":
        return []

    loser = get_loser(game_state)

    return list(filter(
        lambda leader: leader not in game_state.round_state.leaders_used,
        game_state.faction_state[loser].leaders))


class LeaderCapture(Action):
    name = "leader-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "leader-capture"
    ck_faction = "harkonnen"

    @classmethod
    def _check(cls, game_state, faction):
        if not get_capturable_leaders(game_state):
            raise IllegalAction("There must be a capturable leader")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        loser = get_loser(new_game_state)
        choice = new_game_state.random_choice_deck.pop(0)
        capturable_leaders = get_capturable_leaders(new_game_state)
        leader_to_capture = capturable_leaders[choice % len(capturable_leaders)]
        new_game_state.faction_state[loser].leaders.remove(leader_to_capture)
        new_game_state.faction_state["harkonnen"].leaders.append(leader_to_capture)
        new_game_state.faction_state["harkonnen"].leaders_captured.append(leader_to_capture)
        new_game_state.round_state.stage = "main"
        new_game_state.round_state.battles = ops.find_battles(new_game_state)
        return new_game_state


class LeaderCaptureTank(Action):
    name = "leader-capture-tank"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "leader-capture"
    ck_faction = "harkonnen"

    @classmethod
    def _check(cls, game_state, faction):
        if not get_capturable_leaders(game_state):
            raise IllegalAction("There must be a capturable leader")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        loser = get_loser(new_game_state)
        choice = new_game_state.random_choice_deck.pop(0)
        capturable_leaders = get_capturable_leaders(new_game_state)
        leader_to_tank = capturable_leaders[choice % len(capturable_leaders)]
        ops.tank_leader(new_game_state, loser, leader_to_tank)
        game_state.faction_state["harkonnen"].spice += 2
        new_game_state.round_state.stage = "main"
        new_game_state.round_state.battles = ops.find_battles(new_game_state)
        return new_game_state


class PassLeaderCapture(Action):
    name = "pass-leader-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "leader-capture"
    ck_faction = "harkonnen"

    @classmethod
    def _check(cls, game_state, faction):
        if not get_capturable_leaders(game_state):
            raise IllegalAction("There must be a capturable leader")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage = "main"
        new_game_state.round_state.battles = ops.find_battles(new_game_state)
        return new_game_state


class SkipLeaderCapture(Action):
    name = "skip-leader-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "leader-capture"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if get_capturable_leaders(game_state):
            raise IllegalAction("Harkonnen can capture a leader")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage = "main"
        new_game_state.round_state.battles = ops.find_battles(new_game_state)
        return new_game_state


class KaramaLeaderCapture(Action):
    name = "karama-leader-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-leader-capture"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.stage_state.karama_leader_capture_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.battles = ops.find_battles(new_game_state)
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaPassLeaderCapture(Action):
    name = "karama-pass-leader-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-leader-capture"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "harkonnen":
            raise IllegalAction("You cannot karam your own leader capture!")
        if faction in game_state.round_state.stage_state.karama_leader_capture_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_leader_capture_passes.append(self.faction)
        return new_game_state


class SkipKaramaLeaderCapture(Action):
    name = "skip-karama-leader-capture"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-leader-capture"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if get_capturable_leaders(game_state):
            if len(game_state.round_state.stage_state.karama_leader_capture_passes) != len(game_state.faction_state) - 1:
                raise IllegalAction("Still waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "leader-capture"
        return new_game_state
