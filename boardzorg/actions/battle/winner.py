from copy import deepcopy
from logging import getLogger

from boardzorg.actions import args
from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.actions.battle import ops

logger = getLogger(__name__)


class LostMinions(Action):
    name = "lost-minions"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "winner"

    @classmethod
    def parse_args(cls, faction, args):
        groups = []
        for g in args.split(" "):
            sector, minions = g.split(":")
            minions = [int(u) for u in minions.split(",")]
            sector = int(sector)
            groups.append((sector, minions))
        return LostMinions(faction, groups)

    @classmethod
    def get_arg_spec(cls, faction, game_state=None):
        return args.LostMinions()

    def __init__(self, faction, groups):
        self.faction = faction
        self.groups = groups

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.winner:
            raise IllegalAction("You need to be the winner yo")
        if not game_state.round_state.stage_state.substage_state.power_left_to_lost:
            raise IllegalAction("No power left to lost")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        space = new_game_state.map_state[battle_id[2]]
        for sector, minions in self.groups:
            if sector not in space.forces[self.faction]:
                raise BadCommand("Bad sector {}".format(sector))
            for u in minions:
                if new_game_state.round_state.stage_state.substage_state.power_left_to_lost <= 0:
                    raise BadCommand("Losting too many minions")
                new_game_state.round_state.stage_state.substage_state.power_left_to_lost -= u
                ops.lost_minion(new_game_state, self.faction, space, sector, u)

        return new_game_state


class DiscardProvisions(Action):
    name = "discard"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "winner"

    @classmethod
    def parse_args(cls, faction, args):
        weapon = "weapon" in args
        defense = "defense" in args
        return DiscardProvisions(faction, weapon, defense)

    def __init__(self, faction, weapon, defense):
        self.faction = faction
        self.weapon = weapon
        self.defense = defense

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.DiscardProvisions()

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.winner:
            raise IllegalAction("You need to be the winner yo")
        if game_state.round_state.stage_state.substage_state.discard_done:
            raise IllegalAction("You already discarded or kept these cards")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        ss = new_game_state.round_state.stage_state
        fs = new_game_state.faction_state[self.faction]
        winner_is_attacker = ss.winner == ss.battle[0]
        winner_plan = ss.attacker_plan if (ss.winner == ss.battle[0]) else ss.defender_plan

        def _do_discard(do_it, kind):
            if do_it:
                if winner_plan[kind] is not None:
                    ops.discard_provisions(new_game_state, winner_plan[kind])
            elif winner_plan[kind] is not None:
                fs.provisions.append(winner_plan[kind])

        _do_discard(self.weapon, "weapon")
        _do_discard(self.defense, "defense")

        ss.substage_state.discard_done = True

        return new_game_state


class ConcludeWinner(Action):
    name = "conclude-winner"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "winner"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.stage_state.substage_state.discard_done:
            ss = game_state.round_state.stage_state
            winner_plan = ss.attacker_plan if (ss.winner == ss.battle[0]) else ss.defender_plan
            if winner_plan["weapon"] or winner_plan["defense"]:
                raise IllegalAction("Winner must decide what to discard if anything")
        if game_state.round_state.stage_state.substage_state.power_left_to_lost > 0:
            raise IllegalAction("Winner must still lost some minions")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        # Return captured character if used
        [attacker, defender, space, _] = new_game_state.round_state.stage_state.battle
        attacker_plan = new_game_state.round_state.stage_state.attacker_plan
        defender_plan = new_game_state.round_state.stage_state.defender_plan
        if attacker_plan["character"] in new_game_state.faction_state[attacker].characters_captured:
            ops.return_character(new_game_state, capturing_faction=attacker, character=attacker_plan["character"])
        if defender_plan["character"] in new_game_state.faction_state[defender].characters_captured:
            ops.return_character(new_game_state, capturing_faction=defender, character=defender_plan["character"])

        space = new_game_state.map_state[space]
        # If rabbit not present or alone, there can be no frends_and_raletions
        if "rabbit" not in space.forces or len(space.forces) == 1:
            space.chill_out = False

        new_game_state.round_state.stage_state.substage = "author-character-capture"
        return new_game_state
