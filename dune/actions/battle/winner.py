from copy import deepcopy
from logging import getLogger

from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.actions.battle import ops

logger = getLogger(__name__)


class TankUnits(Action):
    name = "tank-units"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "winner"

    @classmethod
    def parse_args(cls, faction, args):
        groups = []
        for g in args.split(" "):
            sector, units = g.split(":")
            units = [int(u) for u in units.split(",")]
            sector = int(sector)
            groups.append((sector, units))
        return TankUnits(faction, groups)

    def __init__(self, faction, groups):
        self.faction = faction
        self.groups = groups

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.winner:
            raise IllegalAction("You need to be the winner yo")
        if not game_state.round_state.stage_state.substage_state.power_left_to_tank:
            raise IllegalAction("No power left to tank")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        space = new_game_state.map_state[battle_id[2]]
        for sector, units in self.groups:
            if sector not in space.forces[self.faction]:
                raise BadCommand("Bad sector {}".format(sector))
            for u in units:
                if new_game_state.round_state.stage_state.substage_state.power_left_to_tank <= 0:
                    raise BadCommand("Tanking too many units")
                new_game_state.round_state.stage_state.substage_state.power_left_to_tank -= u
                ops.tank_unit(new_game_state, self.faction, space, sector, u)

        return new_game_state


class DiscardTreachery(Action):
    name = "discard"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "winner"

    @classmethod
    def parse_args(cls, faction, args):
        weapon = "weapon" in args
        defense = "defense" in args
        return DiscardTreachery(faction, weapon, defense)

    def __init__(self, faction, weapon, defense):
        self.faction = faction
        self.weapon = weapon
        self.defense = defense

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

        if self.weapon:
            if winner_is_attacker:
                ops.discard_treachery(new_game_state, ss.attacker_plan["weapon"])
            else:
                ops.discard_treachery(new_game_state, ss.defender_plan["weapon"])
        else:
            if winner_is_attacker:
                fs.treachery.append(ss.attacker_plan["weapon"])
            else:
                fs.treachery.append(ss.defender_plan["weapon"])

        if self.defense:
            if winner_is_attacker:
                ops.discard_treachery(new_game_state, ss.attacker_plan["defense"])
            else:
                ops.discard_treachery(new_game_state, ss.defender_plan["defense"])
        else:
            if winner_is_attacker:
                fs.treachery.append(ss.attacker_plan["defense"])
            else:
                fs.treachery.append(ss.defender_plan["defense"])

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
            raise IllegalAction("Winner must decide what to discard if anything")
        if game_state.round_state.stage_state.substage_state.power_left_to_tank > 0:
            raise IllegalAction("Winner must still tank some units")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.stage = "main"
        return new_game_state
