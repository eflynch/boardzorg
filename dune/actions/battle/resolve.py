from copy import deepcopy
from logging import getLogger

from dune.actions import args
from dune.actions.action import Action
from dune.state.rounds import battle
from dune.exceptions import IllegalAction, BadCommand
from dune.state.leaders import get_leader_faction
from dune.actions.battle import ops
from dune.actions.battle.winner import DiscardTreachery, TankUnits

logger = getLogger(__name__)


class CommitPlan(Action):
    name = "commit-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "finalize"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) != 4:
            raise BadCommand("Need four values")
        leader, number, weapon, defense = parts
        if weapon == "-":
            weapon = None
        if defense == "-":
            defense = None
        number = int(number)
        return CommitPlan(faction, leader, number, weapon, defense)

    def __init__(self, faction, leader, number, weapon, defense):
        self.faction = faction
        self.leader = leader
        self.number = number
        self.weapon = weapon
        self.defense = defense

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.BattlePlan(faction=faction, max_power=ops.compute_max_power_faction(game_state, faction))

    @classmethod
    def _check(cls, game_state, faction):
        if faction not in game_state.round_state.stage_state.battle:
            raise IllegalAction("You are not in this battle")
        if faction == game_state.round_state.stage_state.battle[0]:
            if len(game_state.round_state.stage_state.attacker_plan) == 4:
                raise IllegalAction("You are already committed in this battle")
        else:
            if len(game_state.round_state.stage_state.defender_plan) == 4:
                raise IllegalAction("You are already committed in this battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        stage_state = new_game_state.round_state.stage_state
        battle_id = new_game_state.round_state.stage_state.battle
        is_attacker = (self.faction == battle_id[0])

        max_power = ops.compute_max_power_faction(new_game_state, self.faction)

        ops.pick_leader(new_game_state, is_attacker, self.leader)
        ops.pick_number(new_game_state, max_power, is_attacker, self.number)
        ops.pick_weapon(new_game_state, is_attacker, self.weapon)
        ops.pick_defense(new_game_state, is_attacker, self.defense)

        return new_game_state


class RevealEntire(CommitPlan):
    name = "reveal-plan"
    ck_substage = "reveal-entire"

    def _execute(self, game_state):
        new_game_state = super()._execute(game_state)
        is_attacker = False
        if self.faction == new_game_state.round_state.stage_state.battle[0]:
            is_attacker = True
        new_game_state.round_state.stage_state.reveal_entire = True
        new_game_state.round_state.stage_state.reval_entire_is_attacker = is_attacker
        new_game_state.round_state.stage_state.substage = "karama-kwizatz-haderach"
        return new_game_state


class RevealPlans(Action):
    name = "reveal-plans"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "finalize"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.attacker_plan) != 4:
            raise IllegalAction("Waiting for the attacker to define their plan")
        if len(game_state.round_state.stage_state.defender_plan) != 4:
            raise IllegalAction("Waiting for the defender to define their plan")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "traitors"
        [attacker, defender, _, _] = new_game_state.round_state.stage_state.battle

        def _maybe_remove_item(game_state, plan, faction, kind):
            if plan[kind] is not None:
                game_state.faction_state[faction].treachery.remove(plan[kind])

        _maybe_remove_item(new_game_state, new_game_state.round_state.stage_state.attacker_plan,
                           attacker, "weapon")
        _maybe_remove_item(new_game_state, new_game_state.round_state.stage_state.attacker_plan,
                           attacker, "defense")
        _maybe_remove_item(new_game_state, new_game_state.round_state.stage_state.defender_plan,
                           defender, "weapon")
        _maybe_remove_item(new_game_state, new_game_state.round_state.stage_state.defender_plan,
                           defender, "defense")
        return new_game_state


class RevealTraitor(Action):
    name = "reveal-traitor"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "traitors"

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.stage_state.traitor_revealers:
            raise IllegalAction("You already revealed your traitor")
        if faction in game_state.round_state.stage_state.traitor_passes:
            raise IllegalAction("You already passed your traitor")
        battle_id = game_state.round_state.stage_state.battle

        if faction == battle_id[0]:
            leader = game_state.round_state.stage_state.defender_plan["leader"]
        elif faction == battle_id[1]:
            leader = game_state.round_state.stage_state.attacker_plan["leader"]
        else:
            if faction != "harkonnen":
                raise IllegalAction("Only the Harkonnen can reveal traitors for others")

            if faction in game_state.alliances[battle_id[0]]:
                leader = game_state.round_state.stage_state.defender_plan["leader"]
            elif faction in game_state.alliances[battle_id[1]]:
                leader = game_state.round_state.stage_state.attacker_plan["leader"]
            else:
                raise IllegalAction("You are not allies with the embattled")

        if leader not in game_state.faction_state[faction].traitors:
            raise IllegalAction("That leader is not in your pay!")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        stage_state = new_game_state.round_state.stage_state
        battle_id = stage_state.battle
        stage_state.traitor_revealers.append(self.faction)
        return new_game_state


class AutoResolveWithTraitor(Action):
    name = "resolve-reveal-traitor"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "resolve"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        battle_id = game_state.round_state.stage_state.battle
        if len(game_state.round_state.stage_state.traitor_passes) != 1:
            raise IllegalAction("Still have to see if there is another traitor")
        if len(game_state.round_state.stage_state.traitor_revealers) != 1:
            raise IllegalAction("Not exactly one traitor has been revealed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        stage_state = new_game_state.round_state.stage_state
        battle_id = stage_state.battle
        space = new_game_state.map_state[battle_id[2]]

        if self.faction == battle_id[0]:
            winner = battle_id[0]
            loser = battle_id[1]
            ops.discard_treachery(new_game_state, stage_state.defender_plan["weapon"])
            ops.discard_treachery(new_game_state, stage_state.defender_plan["defense"])
            ops.tank_leader(new_game_state, loser, stage_state.defender_plan["leader"])
            new_game_state.faction_state[winner].spice += stage_state.defender_plan["leader"][1]
        else:
            winner = battle_id[1]
            loser = battle_id[0]
            ops.discard_treachery(new_game_state, stage_state.attacker_plan["weapon"])
            ops.discard_treachery(new_game_state, stage_state.attacker_plan["defense"])
            ops.tank_leader(new_game_state, loser, stage_state.attacker_plan["leader"])
            new_game_state.faction_state[winner].spice += stage_state.attacker_plan["leader"][1]

        for sec in space.forces[loser]:
            units_to_tank = space.forces[loser][sec][:]
            for u in units_to_tank:
                ops.tank_unit(new_game_state, loser, space, sec, u)

        new_game_state.round_state.stage_state.winner = winner
        new_game_state.pause.append(loser)
        new_game_state.round_state.stage_state.substage_state = battle.WinnerSubStage()
        new_game_state.round_state.stage_state.substage_state.power_left_to_tank = 0
        return new_game_state


class PassRevealTraitor(Action):
    name = "pass-reveal-traitor"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "traitors"

    @classmethod
    def _check(cls, game_state, faction):
        battle_id = game_state.round_state.stage_state.battle

        if faction not in battle_id:
            raise IllegalAction("You don't even go here")
        if faction in game_state.round_state.stage_state.traitor_passes:
            raise IllegalAction("You already passed yo")
        if faction in game_state.round_state.stage_state.traitor_revealers:
            raise IllegalAction("You already revealed yo")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.traitor_passes.append(self.faction)
        return new_game_state


class SkipRevealTraitor(Action):
    name = "skip-reveal-traitor"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "traitors"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.traitor_passes) + len(game_state.round_state.stage_state.traitor_revealers) != 2:
            raise IllegalAction("Still waiting on traitor passes and reveals")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "resolve"
        return new_game_state


class AutoResolveDisaster(Action):
    name = "auto-disaster"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "resolve"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        double_traitor = game_state.round_state.stage_state.traitor_revealers == 2

        battle_id = game_state.round_state.stage_state.battle
        stage_state = game_state.round_state.stage_state
        # Check for Lasgun-Shield Explosion
        has_lasgun = "Lasgun" in stage_state.attacker_plan.values() or "Lasgun" in stage_state.defender_plan.values()
        has_shield = "Shield" in stage_state.attacker_plan.values() or "Shield" in stage_state.defender_plan.values()

        if not double_traitor or not (has_lasgun and has_shield):
            raise IllegalAction("No auto resolve if we don't have a bang")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        stage_state = new_game_state.round_state.stage_state

        has_lasgun = "Lasgun" in stage_state.attacker_plan.values() or "Lasgun" in stage_state.defender_plan.values()
        has_shield = "Shield" in stage_state.attacker_plan.values() or "Shield" in stage_state.defender_plan.values()

        # Tank All units and leaders in battle
        space = new_game_state.map_state[battle_id[2]]
        for faction in battle_id[:2]:
            for sec in space.forces[faction]:
                # TODO : Check distance to sector from battle sector is 0
                units_to_tank = space.forces[faction][sec][:]
                for u in units_to_tank:
                    ops.tank_unit(new_game_state, faction, space, sec, u)
        ops.tank_leader(new_game_state, battle_id[0], stage_state.attacker_plan["leader"])
        ops.tank_leader(new_game_state, battle_id[1], stage_state.defender_plan["leader"])

        # If explosion tank all other units and leaders in the sector too
        if has_lasgun and has_shield:
            space = new_game_state.map_state[battle_id[2]]
            space.coexist = False
            for fac in space.forces:
                for sec in space.forces[fac]:
                    units_to_tank = space.forces[fac][sec][:]
                    for u in units_to_tank:
                        ops.tank_unit(new_game_state, fac, space, sec, u)

            for leader_name in new_game_state.round_state.leaders_used:
                space, sector = new_game_state.round_state.leaders_used[leader_name]["location"]
                leader = new_game_state.round_state.leaders_used[leader_name]["leader"]
                if space == battle_id[2]:
                    if leader != stage_state.attacker_plan["leader"]:
                        if leader != stage_state.defender_plan["leader"]:
                            faction = get_leader_faction(leader)
                            ops.tank_leader(new_game_state, faction, leader)

        # Discard all treachery
        ops.discard_treachery(new_game_state, stage_state.attacker_plan["weapon"])
        ops.discard_treachery(new_game_state, stage_state.attacker_plan["defense"])
        ops.discard_treachery(new_game_state, stage_state.defender_plan["weapon"])
        ops.discard_treachery(new_game_state, stage_state.defender_plan["defense"])

        new_game_state.pause.extend(battle_id[:2])
        new_game_state.round_state.stage = "main"
        return new_game_state


class AutoResolve(Action):
    name = "auto-resolve"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "resolve"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.traitor_revealers:
            raise IllegalAction("Cannot auto resolve with a traitor in the mix")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        stage_state = new_game_state.round_state.stage_state

        attacker_power = 0
        defender_power = 0
        dead_leaders = []

        def clash_leaders(plan_a, plan_b, faction_b, location):
            if plan_b["leader"] == "Cheap-Hero/Heroine":
                return 0

            if ops.clash_weapons(plan_a["weapon"], plan_b["defense"]):
                ops.tank_leader(new_game_state, faction_b, plan_b["leader"])
                dead_leaders.append(plan_b["leader"])
                return 0

            new_game_state.round_state.leaders_used[plan_b["leader"][0]] = {
                "location": location,
                "leader": plan_b["leader"]
            }
            return plan_b["leader"][1]

        attacker_power += clash_leaders(stage_state.defender_plan, stage_state.attacker_plan, battle_id[0], (battle_id[2], battle_id[3]))
        defender_power += clash_leaders(stage_state.attacker_plan, stage_state.defender_plan, battle_id[1], (battle_id[2], battle_id[3]))

        space = new_game_state.map_state[battle_id[2]]

        attacker_max_power, defender_max_power = ops.compute_max_powers(new_game_state)
        attacker_power += min(attacker_max_power, stage_state.attacker_plan["number"])
        defender_power += min(defender_max_power, stage_state.defender_plan["number"])

        if attacker_power >= defender_power:
            winner = battle_id[0]
            loser = battle_id[1]
            ops.discard_treachery(new_game_state, stage_state.defender_plan["weapon"])
            ops.discard_treachery(new_game_state, stage_state.defender_plan["defense"])
            power_left_to_tank = min(attacker_max_power, stage_state.attacker_plan["number"])
        else:
            winner = battle_id[1]
            loser = battle_id[0]
            ops.discard_treachery(new_game_state, stage_state.attacker_plan["weapon"])
            ops.discard_treachery(new_game_state, stage_state.attacker_plan["defense"])
            power_left_to_tank = min(defender_max_power, stage_state.defender_plan["number"])

        for sec in space.forces[loser]:
            # TODO : Check distance to sector from battle sector is 0
            units_to_tank = space.forces[loser][sec][:]
            for u in units_to_tank:
                ops.tank_unit(new_game_state, loser, space, sec, u)

        # Pay Winner Spice for dead leaders
        for (_, value) in dead_leaders:
            new_game_state.faction_state[winner].spice += value

        # Winner Must Tank Units (increase KH count if atreides)
        # Winner Must decide whether to discard treachery (return remaining ones to winner)

        new_game_state.pause.append(loser)
        new_game_state.round_state.stage_state.winner = winner
        new_game_state.round_state.stage_state.substage_state = battle.WinnerSubStage()
        new_game_state.round_state.stage_state.substage_state.power_left_to_tank = power_left_to_tank
        return new_game_state
