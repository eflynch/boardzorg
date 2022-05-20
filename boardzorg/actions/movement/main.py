from copy import deepcopy
import math

from boardzorg.actions.action import Action
from boardzorg.actions.common import get_faction_order
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.rounds import movement, battle
from boardzorg.map.map import MapGraph
from boardzorg.actions.karama import discard_karama
from boardzorg.actions.battle import ops


class KaramaBlockGuildTurnChoice(Action):
    name = "karama-block-guild-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"
    ck_karama = True

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "guild":
            raise IllegalAction("The guild cannot do that")
        if faction in game_state.round_state.stage_state.karama_passes:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.guild_choice_blocked = True
        faction_order = get_faction_order(game_state)
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.stage_state = movement.TurnStage()
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaPassBlockGuildTurnChoice(Action):
    name = "karama-pass-block-guild-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "guild":
            raise IllegalAction("The guild cannot do that")
        if faction in game_state.round_state.stage_state.karama_passes:
            raise IllegalAction("You have already passed this option")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_passes.append(self.faction)
        return new_game_state


class SkipKaramaGuildTurnChoice(Action):
    name = "skip-karama-block-guild-turn-choice"
    ck_round = "movement"
    ck_stage = "setup"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "guild" in game_state.faction_state:
            if len(game_state.round_state.stage_state.karama_passes) != len(game_state.faction_state) - 1:
                raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        faction_order = get_faction_order(game_state)
        if "guild" in faction_order:
            faction_order.remove("guild")
            faction_order.insert(0, "guild")
        new_game_state.round_state.turn_order = faction_order
        new_game_state.round_state.faction_turn = faction_order[0]
        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state


class GuildPass(Action):
    name = "guild-pass-turn"
    ck_round = "movement"
    ck_stage = "turn"
    ck_faction = "guild"
    ck_substage = "main"

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)
        if game_state.round_state.guild_choice_blocked:
            raise IllegalAction("The guild choice has been blocked by karama")
        if game_state.round_state.stage_state.shipment_used:
            raise IllegalAction("You have already started your turn")
        if game_state.round_state.stage_state.movement_used:
            raise IllegalAction("You have already started your turn")
        if game_state.round_state.turn_order[-1] == "guild":
            raise IllegalAction("You last fool")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        idx = new_game_state.round_state.turn_order.index("guild")
        new_game_state.round_state.turn_order.remove("guild")
        new_game_state.round_state.turn_order.insert(idx+1, "guild")
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
        # forces in the space as us, and they've moved already, our units get tanked!
        moved_alliances = (alliance for alliance in new_game_state.alliances[self.faction] if
                     new_game_state.round_state.turn_order.index(alliance) < idx)
        for space in new_game_state.map_state.values():
            if (self.faction in space.forces and
                any((alliance in space.forces for alliance in moved_alliances))):
                    sectors = list(space.forces[self.faction].keys())
                    for sec in sectors:
                        for u in space.forces[self.faction][sec][:]:
                            ops.tank_unit(game_state, self.faction, space, sec, u)

        if idx == len(new_game_state.round_state.turn_order) - 1:
            new_game_state.round_state = battle.BattleRound()
            return new_game_state
        new_game_state.round_state.faction_turn = new_game_state.round_state.turn_order[idx + 1]
        new_game_state.round_state.stage_state = movement.TurnStage()
        return new_game_state
