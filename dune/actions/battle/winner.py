from copy import deepcopy
from logging import getLogger

from dune.actions import args
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

    @classmethod
    def get_arg_spec(cls, faction):
        return args.String()

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
        winner_plan = ss.attacker_plan if (ss.winner == ss.battle[0]) else ss.defender_plan

        if self.weapon and winner_plan["weapon"] is not None:
            ops.discard_treachery(new_game_state, winner_plan["weapon"])
        elif winner_plan["weapon"] is not None:
            fs.treachery.append(winner_plan["weapon"])

        if self.defense and winner_plan["defense"] is not None:
            ops.discard_treachery(new_game_state, winner_plan["defense"])
        elif winner_plan["weapon"] is not None:
            fs.treachery.append(winner_plan["defense"])

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
        if game_state.round_state.stage_state.substage_state.power_left_to_tank > 0:
            raise IllegalAction("Winner must still tank some units")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        space = new_game_state.map_state[new_game_state.round_state.stage_state.battle[2]]
        # If bene-gesserit not present or alone, there can be no advisors
        if "bene-gesserit" not in space.forces or len(space.forces) == 1:
            space.coexist = False

        new_game_state.round_state.battles.remove(new_game_state.round_state.stage_state.battle)
        new_game_state.round_state.stage = "main"
        return new_game_state
