from copy import deepcopy
import math

from boardzorg.actions.action import Action
from boardzorg.actions.common import get_faction_order
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.rounds import movement, battle
from boardzorg.map.map import MapGraph
from boardzorg.actions.author import discard_author
from boardzorg.actions.battle import ops


class AuthorBlockKangaTurnChoice(Action):
    name = "author-block-kanga-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"
    ck_author = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "kanga":
            raise IllegalAction("The kanga cannot do that")
        if faction in game_state.round_state.stage_state.author_passes:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.kanga_choice_blocked = True
        faction_order = get_faction_order(game_state)
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.stage_state = movement.TurnStage()
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassBlockKangaTurnChoice(Action):
    name = "author-pass-block-kanga-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "kanga":
            raise IllegalAction("The kanga cannot do that")
        if faction in game_state.round_state.stage_state.author_passes:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.author_passes.append(self.faction)
        return new_game_state


class SkipAuthorKangaTurnChoice(Action):
    name = "skip-author-block-kanga-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "kanga" in game_state.faction_state:
            if len(game_state.round_state.stage_state.author_passes) != len(game_state.faction_state) - 1:
                raise IllegalAction("Waiting for author passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        faction_order = get_faction_order(game_state)
        if "kanga" in faction_order:
            faction_order.remove("kanga")
            faction_order.insert(0, "kanga")
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state


class KangaPass(Action):
    name = "kanga-pass-turn"
    ck_round = "movement"
    ck_stage = "turn"
    ck_faction = "kanga"
    ck_substage = "main"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.kanga_choice_blocked:
            raise IllegalAction("The kanga choice has been blocked by author")
        if game_state.round_state.stage_state.imagination_used:
            raise IllegalAction("You have already started your turn")
        if game_state.round_state.stage_state.movement_used:
            raise IllegalAction("You have already started your turn")
        if game_state.round_state.turn_order[-1] == "kanga":
            raise IllegalAction("You last fool")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        idx = new_game_state.round_state.turn_order.index("kanga")
        new_game_state.round_state.turn_order.remove("kanga")
        new_game_state.round_state.turn_order.insert(idx+1, "kanga")
        new_game_state.round_state.faction_turn = new_game_state.round_state.turn_order[idx]
        return new_game_state


class EndMovementTurn(Action):
    name = "end-movement"
    ck_round = "movement"
    ck_stage = "turn"
    ck_substage = "main"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        idx = new_game_state.round_state.turn_order.index(self.faction)

        # Edge case - if we're in an alliance, and our alliance partner has
        # forces in the space as us, and they've moved already, our minions get losted!
        moved_alliances = (alliance for alliance in new_game_state.alliances[self.faction] if
                     new_game_state.round_state.turn_order.index(alliance) < idx)
        for space in new_game_state.map_state.values():
            if (self.faction in space.forces and
                any((alliance in space.forces for alliance in moved_alliances))):
                    sectors = list(space.forces[self.faction].keys())
                    for sec in sectors:
                        for u in space.forces[self.faction][sec][:]:
                            ops.lost_minion(game_state, self.faction, space, sec, u)

        if idx == len(new_game_state.round_state.turn_order) - 1:
            new_game_state.round_state = battle.BattleRound()
            return new_game_state
        new_game_state.round_state.faction_turn = new_game_state.round_state.turn_order[idx + 1]
        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state
