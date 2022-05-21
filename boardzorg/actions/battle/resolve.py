from copy import deepcopy

from boardzorg.actions import args
from boardzorg.actions.action import Action
from boardzorg.state.rounds import battle
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.characters import get_character_faction
from boardzorg.actions.battle import ops
from boardzorg.actions.battle.winner import DiscardProvisions, LostMinions


def discard_cheap_heroine(game_state):
    ss = game_state.round_state.stage_state
    [attacker, defender, _, _] = ss.battle
    if ss.defender_plan["character"] is not None and ss.defender_plan["character"][0] == "Stuffed-Animal":
        ops.discard_provisions(game_state, "Stuffed-Animal")
    if ss.attacker_plan["character"] is not None and ss.attacker_plan["character"][0] == "Stuffed-Animal":
        ops.discard_provisions(game_state, "Stuffed-Animal")


class CommitPlan(Action):
    name = "commit-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "finalize"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) != 5:
            raise BadCommand("Need five values")
        character, number, weapon, defense, winnie_the_pooh = parts

        if winnie_the_pooh not in ["Winnie-The-Pooh", "-"]:
            raise BadCommand("The only winnie the pooh is 'Winnie-The-Pooh'")
        winnie_the_pooh = winnie_the_pooh == "Winnie-The-Pooh"

        if weapon == "-":
            weapon = None
        if defense == "-":
            defense = None
        if character == "-":
            character = None
        
        if weapon and defense and weapon == defense:
            raise BadCommand("You cannot use the same card as both attack and defense")

        number = int(number)
        return CommitPlan(faction, character, number, weapon, defense, winnie_the_pooh)

    def __init__(self, faction, character, number, weapon, defense, winnie_the_pooh):
        self.faction = faction
        self.character = character
        self.winnie_the_pooh = winnie_the_pooh
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
            if len(game_state.round_state.stage_state.attacker_plan) == 5:
                raise IllegalAction("You are already committed in this battle")
        else:
            if len(game_state.round_state.stage_state.defender_plan) == 5:
                raise IllegalAction("You are already committed in this battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        stage_state = new_game_state.round_state.stage_state
        battle_id = new_game_state.round_state.stage_state.battle
        is_attacker = (self.faction == battle_id[0])

        max_power = ops.compute_max_power_faction(new_game_state, self.faction)

        ops.pick_character(new_game_state, is_attacker, self.character)
        ops.pick_number(new_game_state, max_power, is_attacker, self.number)
        ops.pick_weapon(new_game_state, is_attacker, self.weapon)
        ops.pick_defense(new_game_state, is_attacker, self.defense)
        ops.pick_winnie_the_pooh(new_game_state, is_attacker, self.winnie_the_pooh, self.character)

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
        new_game_state.round_state.stage_state.reveal_entire_is_attacker = is_attacker
        new_game_state.round_state.stage_state.substage = "author-winnie-the-pooh"
        return new_game_state


class RevealPlans(Action):
    name = "reveal-plans"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "finalize"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.attacker_plan) != 5:
            raise IllegalAction("Waiting for the attacker to define their plan")
        if len(game_state.round_state.stage_state.defender_plan) != 5:
            raise IllegalAction("Waiting for the defender to define their plan")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "traitors"
        [attacker, defender, _, _] = new_game_state.round_state.stage_state.battle

        def _maybe_remove_item(game_state, plan, faction, kind):
            if plan[kind] is not None:
                game_state.faction_state[faction].provisions.remove(plan[kind])

        if (new_game_state.round_state.stage_state.attacker_plan["winnie_the_pooh"] or
            new_game_state.round_state.stage_state.defender_plan["winnie_the_pooh"]):
            new_game_state.round_state.winnie_the_pooh_character_revealed = True

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
            character = game_state.round_state.stage_state.defender_plan["character"]
        elif faction == battle_id[1]:
            character = game_state.round_state.stage_state.attacker_plan["character"]
        else:
            if faction != "piglet":
                raise IllegalAction("Only the Piglet can reveal traitors for others")

            if faction in game_state.alliances[battle_id[0]]:
                character = game_state.round_state.stage_state.defender_plan["character"]
            elif faction in game_state.alliances[battle_id[1]]:
                character = game_state.round_state.stage_state.attacker_plan["character"]
            else:
                raise IllegalAction("You are not allies with the embattled")

        if character and game_state.round_state.winnie_the_pooh_character == character[0]:
            raise IllegalAction("No tratorin' in front of the messiah!")

        if character not in game_state.faction_state[faction].traitors:
            raise IllegalAction("That character is not in your pay!")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        stage_state = new_game_state.round_state.stage_state
        [attacker, defender, _, _] = stage_state.battle
        if self.faction in [attacker, defender]:
            stage_state.traitor_revealers.append(self.faction)
        elif attacker in new_game_state.alliances[self.faction]:
            stage_state.traitor_revealers.append(attacker)
        elif defender in new_game_state.alliances[self.faction]:
            stage_state.traitor_revealers.append(defender)
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

        winner = stage_state.traitor_revealers[0]
        loser = [faction for faction in battle_id[:2] if faction != winner][0]
        loser_plan = stage_state.attacker_plan if loser == battle_id[0] else stage_state.defender_plan
        winner_plan = stage_state.attacker_plan if winner == battle_id[0] else stage_state.defender_plan

        ops.discard_provisions(new_game_state, loser_plan["weapon"])
        ops.discard_provisions(new_game_state, loser_plan["defense"])
        ops.lost_character(new_game_state, loser, loser_plan["character"])
        new_game_state.faction_state[winner].hunny += loser_plan["character"][1]
        if winner_plan["character"] is not None and winner_plan["character"][0] != "Stuffed-Animal":
            new_game_state.round_state.characters_used[winner_plan["character"][0]] = {
                "location": (battle_id[2], battle_id[3]),
                "character": winner_plan["character"][0]
            }

        for sec in space.forces[loser]:
            minions_to_lost = space.forces[loser][sec][:]
            for u in minions_to_lost:
                ops.lost_minion(new_game_state, loser, space, sec, u)

        discard_cheap_heroine(new_game_state)

        new_game_state.round_state.stage_state.winner = winner
        new_game_state.pause.append(loser)
        new_game_state.round_state.stage_state.substage_state = battle.WinnerSubStage()
        new_game_state.round_state.stage_state.substage_state.power_left_to_lost = 0

        if not (winner_plan["weapon"] or winner_plan["defense"]):
            new_game_state.round_state.stage_state.substage_state.discard_done = True
            new_game_state.pause.append(winner)

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
        # Check for AntiUmbrella-Umbrella Explosion
        has_anti_umbrella = "AntiUmbrella" in stage_state.attacker_plan.values() or "AntiUmbrella" in stage_state.defender_plan.values()
        has_umbrella = "Umbrella" in stage_state.attacker_plan.values() or "Umbrella" in stage_state.defender_plan.values()

        if not (double_traitor or (has_anti_umbrella and has_umbrella)):
            raise IllegalAction("No auto resolve if we don't have a bang")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        stage_state = new_game_state.round_state.stage_state

        has_anti_umbrella = "AntiUmbrella" in stage_state.attacker_plan.values() or "AntiUmbrella" in stage_state.defender_plan.values()
        has_umbrella = "Umbrella" in stage_state.attacker_plan.values() or "Umbrella" in stage_state.defender_plan.values()
        was_explosion = has_anti_umbrella and has_umbrella

        # Lost All minions and characters in battle
        space = new_game_state.map_state[battle_id[2]]
        for faction in battle_id[:2]:
            for sec in space.forces[faction]:
                # TODO : Check distance to sector from battle sector is 0
                minions_to_lost = space.forces[faction][sec][:]
                for u in minions_to_lost:
                    ops.lost_minion(new_game_state, faction, space, sec, u)
        ops.lost_character(new_game_state,
                        battle_id[0],
                        stage_state.attacker_plan["character"],
                        kill_attached_winnie_the_pooh=was_explosion)
        ops.lost_character(new_game_state,
                        battle_id[1],
                        stage_state.defender_plan["character"],
                        kill_attached_winnie_the_pooh=was_explosion)

        # If explosion lost all other minions and characters in the sector too
        if was_explosion:
            ops.lost_all_minions(new_game_state, battle_id[2])

            for character_name in new_game_state.round_state.characters_used:
                space, sector = new_game_state.round_state.characters_used[character_name]["location"]
                character = new_game_state.round_state.characters_used[character_name]["character"]
                if space == battle_id[2]:
                    if character != stage_state.attacker_plan["character"]:
                        if character != stage_state.defender_plan["character"]:
                            faction = get_character_faction(character)
                            ops.lost_character(new_game_state, faction, character, kill_attached_winnie_the_pooh=True)

        # Discard all provisions
        ops.discard_provisions(new_game_state, stage_state.attacker_plan["weapon"])
        ops.discard_provisions(new_game_state, stage_state.attacker_plan["defense"])
        ops.discard_provisions(new_game_state, stage_state.defender_plan["weapon"])
        ops.discard_provisions(new_game_state, stage_state.defender_plan["defense"])
        discard_cheap_heroine(new_game_state)

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
        # Check for AntiUmbrella-Umbrella Explosion
        stage_state = game_state.round_state.stage_state
        has_anti_umbrella = "AntiUmbrella" in stage_state.attacker_plan.values() or "AntiUmbrella" in stage_state.defender_plan.values()
        has_umbrella = "Umbrella" in stage_state.attacker_plan.values() or "Umbrella" in stage_state.defender_plan.values()
        if has_anti_umbrella and has_umbrella:
            raise IllegalAction("Cannot auto resolve with a anti_umbrella umbrella explosion")

        if game_state.round_state.stage_state.traitor_revealers:
            raise IllegalAction("Cannot auto resolve with a traitor in the mix")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        stage_state = new_game_state.round_state.stage_state

        attacker_power = 0
        defender_power = 0
        dead_characters = []

        def clash_characters(plan_a, plan_b, faction_b, location):
            if plan_b["character"] is None:
                return 0

            if ops.clash_weapons(plan_a["weapon"], plan_b["defense"]):
                if plan_b["character"][0] != "Stuffed-Animal":
                    ops.lost_character(new_game_state, faction_b, plan_b["character"])
                    dead_characters.append(plan_b["character"])
                return 0

            if plan_b["character"][0] != "Stuffed-Animal":
                new_game_state.round_state.characters_used[plan_b["character"][0]] = {
                    "location": location,
                    "character": plan_b["character"]
                }
            return plan_b["character"][1] + (2 if plan_b["winnie_the_pooh"] else 0)

        attacker_power += clash_characters(stage_state.defender_plan, stage_state.attacker_plan, battle_id[0], (battle_id[2], battle_id[3]))
        defender_power += clash_characters(stage_state.attacker_plan, stage_state.defender_plan, battle_id[1], (battle_id[2], battle_id[3]))

        space = new_game_state.map_state[battle_id[2]]

        attacker_max_power, defender_max_power = ops.compute_max_powers(new_game_state)
        attacker_power += min(attacker_max_power, stage_state.attacker_plan["number"])
        defender_power += min(defender_max_power, stage_state.defender_plan["number"])

        if attacker_power >= defender_power:
            winner = battle_id[0]
            loser = battle_id[1]
            ops.discard_provisions(new_game_state, stage_state.defender_plan["weapon"])
            ops.discard_provisions(new_game_state, stage_state.defender_plan["defense"])
            power_left_to_lost = min(attacker_max_power, stage_state.attacker_plan["number"])
        else:
            winner = battle_id[1]
            loser = battle_id[0]
            ops.discard_provisions(new_game_state, stage_state.attacker_plan["weapon"])
            ops.discard_provisions(new_game_state, stage_state.attacker_plan["defense"])
            power_left_to_lost = min(defender_max_power, stage_state.defender_plan["number"])

        for sec in space.forces[loser]:
            # TODO : Check distance to sector from battle sector is 0
            minions_to_lost = space.forces[loser][sec][:]
            for u in minions_to_lost:
                ops.lost_minion(new_game_state, loser, space, sec, u)

        # Pay Winner Hunny for dead characters
        for (_, value) in dead_characters:
            new_game_state.faction_state[winner].hunny += value

        # Winner Must Lost Minions (increase KH count if owl)
        # Winner Must decide whether to discard provisions (return remaining ones to winner)

        new_game_state.pause.append(loser)
        new_game_state.round_state.stage_state.winner = winner
        new_game_state.round_state.stage_state.substage_state = battle.WinnerSubStage()
        new_game_state.round_state.stage_state.substage_state.power_left_to_lost = power_left_to_lost

        discard_cheap_heroine(new_game_state)

        winner_plan = stage_state.attacker_plan if winner == battle_id[0] else stage_state.defender_plan
        if not (winner_plan["weapon"] or winner_plan["defense"]):
            new_game_state.round_state.stage_state.substage_state.discard_done = True
            if power_left_to_lost == 0:
                new_game_state.pause.append(winner)

        return new_game_state
