from copy import deepcopy
from logging import getLogger

from dune.actions.action import Action
from dune.actions import storm
from dune.state.rounds import battle, collection
from dune.exceptions import IllegalAction, BadCommand
from dune.map.map import MapGraph
from dune.state.leaders import parse_leader, get_leader_faction
from dune.state.treachery_cards import WEAPONS, DEFENSES, WORTHLESS
from dune.state.treachery_cards import PROJECTILE_WEAPONS, POISON_WEAPONS, PROJECTILE_DEFENSES, POISON_DEFENSES

logger = getLogger(__name__)


def get_min_sector_map(game_state, space, faction):
    m = MapGraph()
    m.remove_sector(game_state.storm_position)
    force_sector_list = list(space.forces[faction].keys())
    if game_state.storm_position in force_sector_list:
        force_sector_list.remove(game_state.storm_position)
    force_sector_list.sort()
    min_sectors = {}
    for s in force_sector_list:
        for msec in space.sectors:
            if m.distance(space, msec, space, s) == 0:
                if msec not in min_sectors:
                    min_sectors[msec] = []
                min_sectors[msec].append(s)
                break
    return min_sectors


def find_battles(game_state):
    faction_order = storm.get_faction_order(game_state)
    battles = []

    for s in game_state.map_state:
        space = game_state.map_state[s]
        forces = list(space.forces.keys())
        if "bene-gesserit" in forces and space.coexist:
            forces.remove("bene-gesserit")

        if len(forces) <= 1:
            continue

        # sort forces by storm order
        forces = [f for f in faction_order if f in forces]
        for f in forces:
            for g in forces:
                if f == g:
                    continue
                # (f, g, s, min_sector)
                f_map = get_min_sector_map(game_state, space, f)
                g_map = get_min_sector_map(game_state, space, g)
                for f_msec in f_map:
                    if f_msec in g_map:
                        if (g, f, s, f_msec) not in battles:
                            battles.append((f, g, s, f_msec))
    return battles


def validate_battle(game_state, b):
    f, g, s, sector = b
    space = game_state.map_state[s]
    forces = list(space.forces.keys())
    if "bene_gesserit" in forces and space.coexist:
        forces.remove("bene_gesserit")
    if f not in forces:
        return False
    if g not in forces:
        return False
    f_map = get_min_sector_map(game_state, space, f)
    g_map = get_min_sector_map(game_state, space, g)
    if sector not in f_map:
        return False
    if sector not in g_map:
        return False

    return True


def pick_leader(game_state, is_attacker, leader):
    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
    else:
        faction = battle_id[1]

    if leader == "Cheap-Hero/Heroine":
        if leader not in game_state.faction_state[faction].treachery:
            raise BadCommand("You do not have a Cheap-Hero/Heroine available")

        if is_attacker:
            if "leader" in game_state.round_state.stage_state.attacker_plan:
                if game_state.round_state.stage_state.attacker_plan["leader"] != leader:
                    raise BadCommand("You cannot change the leader in your plan")
            game_state.round_state.stage_state.attacker_plan["leader"] = leader
        else:
            if "leader" in game_state.round_state.stage_state.defender_plan:
                if game_state.round_state.stage_state.defender_plan["leader"] != leader:
                    raise BadCommand("You cannot change the leader in your plan")
            game_state.round_state.stage_state.defender_plan["leader"] = leader
        game_state.faction_state[faction].treachery.remove(leader)
        return

    leader = parse_leader(leader)
    if leader not in game_state.faction_state[faction].leaders:
        raise BadCommand("That leader is not available")

    m = MapGraph()
    m.remove_sector(game_state.storm_position)

    if leader in game_state.round_state.leaders_used:
        space, sector = game_state.round_state.leaders_used[leader]
        if m.distance(space, sector, battle_id[2], battle_id[3]) != 0:
            raise BadCommand("That leader was already used in a battle somewhere else")

    if is_attacker:
        if "leader" in game_state.round_state.stage_state.attacker_plan:
            if game_state.round_state.stage_state.attacker_plan["leader"] != leader:
                raise BadCommand("You cannot change the leader in your plan")
        game_state.round_state.stage_state.attacker_plan["leader"] = leader
    else:
        if "leader" in game_state.round_state.stage_state.defender_plan:
            if game_state.round_state.stage_state.defender_plan["leader"] != leader:
                raise BadCommand("You cannot change the leader in your plan")
        game_state.round_state.stage_state.defender_plan["leader"] = leader


def pick_weapon(game_state, is_attacker, weapon):
    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
    else:
        faction = battle_id[1]

    if is_attacker == game_state.round_state.stage_state.voice_is_attacker:
        if game_state.round_state.stage_state.voice is not None:
            (no, poi_proj, weap_def) = game_state.round_state.stage_state.voice
            if weap_def == "weapon":
                if no:
                    if poi_proj == "poison":
                        if weapon in POISON_WEAPONS:
                            raise BadCommand("You were told not to use that one")
                    if poi_proj == "projectile":
                        if weapon in PROJECTILE_WEAPONS:
                            raise BadCommand("You were told not to use that one")
                else:
                    if poi_proj == "poison":
                        if weapon not in POISON_WEAPONS:
                            if (any(w in POISON_WEAPONS for w in game_state.faction_state[faction].treachery)):
                                raise BadCommand("You were told to use your poison weapon")
                    if poi_proj == "projectile":
                        if weapon not in PROJECTILE_WEAPONS:
                            if (any(w in PROJECTILE_WEAPONS for w in game_state.faction_state[faction].treachery)):
                                raise BadCommand("You were told to use your poison weapon")

    if weapon is not None and weapon not in game_state.faction_state[faction].treachery:
        raise BadCommand("That weapon card is not available to you")
    if weapon is not None and weapon not in WEAPONS and weapon not in WORTHLESS:
        raise BadCommand("That card cannot be played as a weapon")

    if is_attacker:
        if "weapon" in game_state.round_state.stage_state.attacker_plan:
            if game_state.round_state.stage_state.attacker_plan["weapon"] != weapon:
                raise BadCommand("You cannot change the weapon in your plan")
        game_state.round_state.stage_state.attacker_plan["weapon"] = weapon
    else:
        if "weapon" in game_state.round_state.stage_state.defender_plan:
            if game_state.round_state.stage_state.defender_plan["weapon"] != weapon:
                raise BadCommand("You cannot change the weapon in your plan")
        game_state.round_state.stage_state.defender_plan["weapon"] = weapon
    if weapon is not None:
        game_state.faction_state[faction].treachery.remove(weapon)


def pick_defense(game_state, is_attacker, defense):
    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
    else:
        faction = battle_id[1]

    if is_attacker == game_state.round_state.stage_state.voice_is_attacker:
        if game_state.round_state.stage_state.voice is not None:
            (no, poi_proj, weap_def) = game_state.round_state.stage_state.voice
            if weap_def == "defense":
                if no:
                    if poi_proj == "poison":
                        if defense in POISON_DEFENSES:
                            raise BadCommand("You were told not to use that one")
                    if poi_proj == "projectile":
                        if defense in PROJECTILE_DEFENSES:
                            raise BadCommand("You were told not to use that one")
                else:
                    if poi_proj == "poison":
                        if defense not in POISON_DEFENSES:
                            if (any(w in POISON_DEFENSES for w in game_state.faction_state[faction].treachery)):
                                raise BadCommand("You were told to use your poison defense")
                    if poi_proj == "projectile":
                        if defense not in PROJECTILE_DEFENSES:
                            if (any(w in PROJECTILE_DEFENSES for w in game_state.faction_state[faction].treachery)):
                                raise BadCommand("You were told to use your poison defense")

    if defense is not None and defense not in game_state.faction_state[faction].treachery:
        raise BadCommand("That defense card is not available to you")
    if defense is not None and defense not in DEFENSES and defense not in WORTHLESS:
        raise BadCommand("That card cannot be played as a defense")

    if is_attacker:
        if "defense" in game_state.round_state.stage_state.attacker_plan:
            if game_state.round_state.stage_state.attacker_plan["defense"] != defense:
                raise BadCommand("You cannot change the defense in your plan")
        game_state.round_state.stage_state.attacker_plan["defense"] = defense
    else:
        if "defense" in game_state.round_state.stage_state.defender_plan:
            if game_state.round_state.stage_state.defender_plan["defense"] != defense:
                raise BadCommand("You cannot change the defense in your plan")
        game_state.round_state.stage_state.defender_plan["defense"] = defense
    if defense is not None:
        game_state.faction_state[faction].treachery.remove(defense)


def pick_number(game_state, is_attacker, number):
    if number > 20 or number < 0:
        raise BadCommand("Number must be between 0 and 20")
    if is_attacker:
        if "number" in game_state.round_state.stage_state.attacker_plan:
            if game_state.round_state.stage_state.attacker_plan["number"] != number:
                raise BadCommand("You cannot change the number in your battle plan")
        game_state.round_state.stage_state.attacker_plan["number"] = number
    else:
        if "number" in game_state.round_state.stage_state.defender_plan:
            if game_state.round_state.stage_state.defender_plan["number"] != number:
                raise BadCommand("You cannot change the number in your battle plan")
        game_state.round_state.stage_state.defender_plan["number"] = number


def tank_unit(game_state, faction, space, sector, unit):
    faction_state = game_state.faction_state[faction]
    if faction == "atreides":
        faction_state.units_lost += 1
        faction_state.kwizatz_haderach_available = faction_state.units_lost >= 7

    if faction not in space.forces:
        raise BadCommand("No {} units in {}".format(faction, space.name))
    if sector not in space.forces[faction]:
        raise BadCommand("No {} units in {} in sector {}".format(faction, space.name, sector))
    if unit not in space.forces[faction][sector]:
        raise BadCommand("That unit is not there")
    space.forces[faction][sector].remove(unit)

    if all(space.forces[faction][s] == [] for s in space.forces[faction]):
        del space.forces[faction]
    if "bene-gesserit" not in space.forces:
        space.coexist = False
    faction_state.tank_units.append(unit)


def tank_leader(game_state, faction, leader):
    faction_state = game_state.faction_state[faction]
    if leader == "Cheap-Hero/Heroine":
        game_state.treachery_discard.insert(0, "Cheap-Hero/Heroine")
        return

    if leader not in faction_state.leaders:
        raise BadCommand("Leader is not available to tank")
    if leader not in faction_state.leader_death_count:
        faction_state.leader_death_count[leader] = 0

    faction_state.leader_death_count[leader] += 1
    faction_state.leaders.remove(leader)
    faction_state.tank_leaders.append(leader)


class StartBattle(Action):
    name = "start-battle"
    ck_round = "battle"
    ck_stage = "setup"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        new_game_state.round_state.faction_turn = storm.get_faction_order(game_state)[0]
        new_game_state.round_state.battles = find_battles(new_game_state)
        new_game_state.round_state.stage_state = battle.MainStage()

        return new_game_state


class PickBattle(Action):
    name = "pick-battle"
    ck_round = "battle"
    ck_stage = "main"

    @classmethod
    def parse_args(cls, faction, args):
        (space, min_sector, defender) = args.split(" ")
        return PickBattle(faction, space, min_sector, defender)

    def __init__(self, faction, space, min_sector, defender):
        self.faction = faction
        self.battle_id = (faction, defender, space, min_sector)

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_turn(game_state, faction)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if self.battle_id not in game_state.round_state.battles:
            raise BadCommand("There is no fight there")

        (_, defender, s, msec) = self.battle_id
        space = game_state.map_state[s]

        if self.faction not in space.forces:
            raise BadCommand("You have no battle to fight in {}".format(space.name))
        if self.defender not in space.forces:
            raise BadCommand("You cannot fight {} when they aren't around".format(self.defender))

        new_game_state.round_state.stage_state = battle.BattleStage()
        new_game_state.round_state.stage_state.battle = self.battle_id
        return new_game_state


class AutoPickBattle(Action):
    name = "auto-pick-battle"
    ck_round = "battle"
    ck_stage = "main"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.battles) > 1:
            battle_1 = game_state.round_state.battles[0]
            battle_2 = game_state.round_state.battles[1]
            if battle_1[0] == battle_2[0] == game_state.round_state.faction_turn:
                if validate_battle(game_state, battle_1):
                    if validate_battle(game_state, battle_2):
                        raise IllegalAction("There are choices to be made")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        to_prune = []
        for b in new_game_state.round_state.battles:
            if not validate_battle(game_state, b):
                to_prune.append(b)
        for b in to_prune:
            new_game_state.round_state.battles.remove(b)

        if not game_state.round_state.battles:
            new_game_state.round_state = collection.CollectionRound()
            return new_game_state

        battle_1 = game_state.round_state.battles[0]
        if battle_1[0] == game_state.round_state.faction_turn:
            new_game_state.round_state.stage_state = battle.BattleStage()
            new_game_state.round_state.stage_state.battle = battle_1
        else:
            new_game_state.round_state.faction_turn = battle_1[0]
        return new_game_state


class Voice(Action):
    name = "voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "voice"
    ck_faction = "bene-gesserit"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            no, projectile_poison, weapon_defense = parts
            if no != "no":
                raise BadCommand("No means no")
            no = True
        elif len(parts) == 2:
            projectile_poison, weapon_defense = parts
            no = False
        else:
            raise BadCommand("Bad args")

        if projectile_poison not in ["projectile", "poison"]:
            raise BadCommand("Must specify either projectile or poison")
        if weapon_defense not in ["weapon", "defense"]:
            raise BadCommand("Must specify either weapon or defense")

        return Voice(faction, no, projectile_poison, weapon_defense)

    @classmethod
    def _check(cls, game_state, faction):
        if "bene-gesserit" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["bene-gesserit"]:
                if defender not in game_state.alliances["bene-gesserit"]:
                    raise IllegalAction("No legal voice is possible")

    def __init__(self, faction, no, projectile_poison, weapon_defense):
        self.faction = faction
        self.no = no
        self.projectile_poison = projectile_poison
        self.weapon_defense = weapon_defense

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        if self.faction == battle_id[0] or self.faction in new_game_state.alliances[battle_id[0]]:
            new_game_state.round_state.stage_state.voice_is_attacker = False
        elif self.faction == battle_id[1] or self.faction in new_game_state.alliances[battle_id[1]]:
            new_game_state.round_state.stage_state.voice_is_attacker = True
        else:
            raise BadCommand("You ain't voicing no one")

        new_game_state.round_state.stage_state.voice = (
            self.no, self.projectile_poison, self.weapon_defense)
        new_game_state.round_state.stage_state.substage = "karama-voice"
        return new_game_state


class PassVoice(Action):
    name = "pass-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "voice"
    ck_faction = "bene-gesserit"

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-voice"
        return new_game_state


class SkipVoice(Action):
    name = "skip-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "voice"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "bene-gesserit" in game_state.faction_state:
            if "bene-gesserit" in game_state.round_state.stage_state.battle:
                raise IllegalAction("The bene-gesserit may use the voice")
            if "bene-gesserit" in game_state.alliances[game_state.round_state.stage_state.battle[0]]:
                raise IllegalAction("The bene-gesserit may use the voice on behalf of their attacker ally")
            if "bene-gesserit" in game_state.alliances[game_state.round_state.stage_state.battle[1]]:
                raise IllegalAction("The bene-gesserit may use the voice on behalf of their defender ally")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-voice"
        return new_game_state


class KaramaVoice(Action):
    name = "karama-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-voice"

    @classmethod
    def _check(cls, game_state, faction):
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a karama card to do this")
        if faction in game_state.round_state.stage_state.voice_karama_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.voice_is_attacker = False
        new_game_state.round_state.stage_state.voice = None
        new_game_state.round_state.stage_state.substage = "prescience"
        return new_game_state


class KaramaPassVoice(Action):
    name = "karama-pass-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-voice"

    @classmethod
    def _check(cls, game_state, faction):
        if faction in game_state.round_state.stage_state.voice_karama_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.voice_karama_passes.append(self.faction)
        return new_game_state


class SkipKaramaVoice(Action):
    name = "skip-karama-voice"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-voice"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.round_state.stage_state.voice_karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Still waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "prescience"
        return new_game_state


class Prescience(Action):
    name = "prescience"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "prescience"
    ck_faction = "atreides"

    @classmethod
    def parse_args(cls, faction, args):
        part = args
        return Prescience(faction, part)

    def __init__(self, faction, part):
        self.faction = faction
        self.part = part

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        if self.faction == battle_id[0] or self.faction in new_game_state.alliances[battle_id[0]]:
            new_game_state.round_state.stage_state.prescience_is_attacker = False
        elif self.faction == battle_id[1] or self.faction in new_game_state.alliances[battle_id[1]]:
            new_game_state.round_state.stage_state.prescience_is_attacker = True
        else:
            raise BadCommand("You can't do that")
        new_game_state.round_state.stage_state.prescience = self.part
        new_game_state.round_state.stage_state.substage = "karama-prescience"
        return new_game_state


class PresciencePass(Action):
    name = "prescience-pass"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "prescience"
    ck_faction = "atreides"

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-entire"
        return new_game_state


class PrescienceSkip(Action):
    name = "prescience-skip"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "prescience"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" in game_state.faction_state:
            if "atreides" in game_state.round_state.stage_state.battle:
                raise IllegalAction("Cannot skip since atreides are in the battle")
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")
            if defender in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-entire"
        return new_game_state


class AnswerPrescience(Action):
    name = "answer-prescience"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-prescience"

    @classmethod
    def parse_args(cls, faction, args):
        part = args
        return AnswerPrescience(faction, part)

    def __init__(self, faction, part):
        self.faction = faction
        self.part = part

    @classmethod
    def _check(cls, game_state, faction):
        battle_id = game_state.round_state.stage_state.battle
        if game_state.round_state.stage_state.prescience is not None:
            if game_state.round_state.stage_state.prescience_is_attacker:
                if faction != battle_id[0]:
                    raise IllegalAction("Only the embattled can define the future")
            else:
                if faction != battle_id[1]:
                    raise IllegalAction("Only the embattled can define the future")
        else:
            raise IllegalAction("No prescience to answer")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        prescience = new_game_state.round_state.stage_state.prescience
        is_attacker = new_game_state.round_state.stage_state.prescience_is_attacker

        if prescience == "leader":
            pick_leader(new_game_state, is_attacker, self.part)
        elif prescience == "number":
            pick_number(new_game_state, is_attacker, int(self.part))
        elif prescience == "weapon":
            pick_weapon(new_game_state, is_attacker, self.part)
        elif prescience == "defense":
            pick_defense(new_game_state, is_attacker, self.part)
        else:
            raise BadCommand("Something bad happened")

        new_game_state.round_state.stage_state.substage = "karama-entire"
        return new_game_state


class KaramaPrescience(Action):
    name = "karama-prescience"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-prescience"

    @classmethod
    def _check(cls, game_state, faction):
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You do not have a Karama card to play")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.prescience = None
        new_game_state.round_state.stage_state.prescience_is_attacker = False
        new_game_state.round_state.stage_state.substage = "karama-entire"
        return new_game_state


class KaramaEntirePlan(Action):
    name = "karama-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-entire"
    ck_faction = "atreides"

    @classmethod
    def _check(cls, game_state, faction):
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a karama card to do this")
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "reveal-entire"
        return new_game_state


class KaramaPassEntirePlan(Action):
    name = "karama-pass-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-entire"
    ck_faction = "atreides"

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" not in game_state.round_state.stage_state.battle:
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker not in game_state.alliances["atreides"]:
                if defender not in game_state.alliances["atreides"]:
                    raise IllegalAction("No legal prescience is possible")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-kwizatz-haderach"
        return new_game_state


class SkipKaramaEntirePlan(Action):
    name = "skip-karama-entire-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-entire"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" in game_state.faction_state:
            if "atreides" in game_state.round_state.stage_state.battle:
                raise IllegalAction("Cannot skip since atreides are in the battle")
            attacker, defender, _, _ = game_state.round_state.stage_state.battle
            if attacker in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")
            if defender in game_state.alliances["atreides"]:
                raise IllegalAction("Cannot skip because allies of atreides are in the battle")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-kwizatz-haderach"
        return new_game_state


class KaramaKwizatzHaderach(Action):
    name = "karama-kwizatz-haderach"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-kwizatz-haderach"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "atreides":
            raise IllegalAction("You cannot karama your own messiah")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a karama card to do this")
        if "atreides" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No Kwizatz to Haderach")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_kwizatz_haderach = True
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        return new_game_state


class KaramaPassKwizatzHaderach(Action):
    name = "karama-pass-kwizatz-haderach"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-kwizatz-haderach"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "atreides":
            raise IllegalAction("You cannot karama your own messiah")
        if "atreides" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No Kwizatz to Haderach")
        if faction in game_state.round_state.stage_state.karama_kwizatz_haderach_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_kwizatz_haderach_passes.append(self.faction)
        return new_game_state


class SkipKaramaKwizatzHaderach(Action):
    name = "skip-karama-kwizatz-haderach"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-kwizatz-haderach"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "atreides" in game_state.faction_state:
            if "atreides" in game_state.round_state.stage_state.battle:
                if len(game_state.round_state.stage_state.karama_kwizatz_haderach_passes) != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-sardaukar"
        return new_game_state


class KaramaSardaukar(Action):
    name = "karama-sardaukar"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-sardaukar"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "emperor":
            raise IllegalAction("You cannot karama your own slave soldier things")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a karama card to do this")
        if "emperor" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No sar to kar")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_sardaukar = True
        new_game_state.round_state.stage_state.substage = "karama-fedaykin"
        return new_game_state


class KaramaPassSardaukar(Action):
    name = "karama-pass-sardaukar"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-sardaukar"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "emperor":
            raise IllegalAction("You cannot karama your own slave soldier things")
        if "emperor" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No sar to kar")
        if faction in game_state.round_state.stage_state.karama_sardaukar_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_sardaukar_passes.append(self.faction)
        return new_game_state


class SkipKaramaSardaukar(Action):
    name = "skip-karama-sardaukar"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-sardaukar"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "emperor" in game_state.faction_state:
            if "emperor" in game_state.round_state.stage_state.battle:
                if len(game_state.round_state.stage_state.karama_sardaukar_passes) != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "karama-fedaykin"
        return new_game_state


class KaramaFedaykin(Action):
    name = "karama-fedaykin"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-fedaykin"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "fremen":
            raise IllegalAction("You cannot karama your own man dudes")
        if "Karama" not in game_state.faction_state[faction].treachery:
            raise IllegalAction("You need a karama card to do this")
        if "fremen" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("No fedaykin")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_fedaykin = True
        new_game_state.round_state.stage_state.substage = "finalize"
        return new_game_state


class KaramaPassFedaykin(Action):
    name = "karama-pass-fedaykin"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-fedaykin"

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "fremen":
            raise IllegalAction("You cannot karama your own main dudes")
        if "fremen" not in game_state.round_state.stage_state.battle:
            raise IllegalAction("no fedaykin")
        if faction in game_state.round_state.stage_state.karama_fedaykin_passes:
            raise IllegalAction("You have already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.karama_fedaykin_passes.append(self.faction)
        return new_game_state


class SkipKaramaFedaykin(Action):
    name = "skip-karama-fedaykin"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "karama-fedaykin"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "fremen" in game_state.faction_state:
            if "fremen" in game_state.round_state.stage_state.battle:
                if len(game_state.round_state.stage_state.karama_fedaykin_passes) != len(game_state.faction_state) - 1:
                    raise IllegalAction("Waiting for karama passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "finalize"
        return new_game_state


class CommitPlan(Action):
    name = "commit-plan"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "finalize"

    @classmethod
    def parse_args(cls, faction, args):
        leader, number, weapon, defense = args.split(" ")
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
        is_attacker = False
        if self.faction == new_game_state.round_state.stage_state.battle[0]:
            is_attacker = True
        pick_leader(new_game_state, is_attacker, self.leader)
        pick_number(new_game_state, is_attacker, self.number)
        pick_weapon(new_game_state, is_attacker, self.weapon)
        pick_defense(new_game_state, is_attacker, self.defense)

        return new_game_state


class RevealEntire(CommitPlan):
    name = "reveal-plan"
    ck_substage = "reveal-entire"

    def _execute(self, game_state):
        new_game_state = super()._execute(game_state)
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
        return new_game_state


class RevealTraitor(Action):
    name = "reveal-traitor"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "traitors"

    @classmethod
    def _check(cls, game_state, faction):
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
        # Kill Leader
        # Pay spice for leader
        # Tank units (increase kh if relevent)
        # Discard treachery
        new_game_state.round_state.stage_state.winner = None
        new_game_state.round_state.stage_state.substage_state = battle.WinnerSubStage()
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
        if len(game_state.round_state.stage_state.traitor_passes) != 2:
            raise IllegalAction("Still waiting on traitor passes")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage = "resolve"
        return new_game_state


class AutoResolve(Action):
    name = "auto-resolve"
    ck_round = "battle"
    ck_stage = "battle"
    ck_substage = "resolve"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        battle_id = new_game_state.round_state.stage_state.battle
        stage_state = new_game_state.round_state.stage_state
        # Check for Lasgun-Shield Explosion
        if "Lasgun" in stage_state.attacker_plan.values() or "Lasgun" in stage_state.defender_plan.values():
            if "Shield" in stage_state.attacker_plan.values() or "Shield" in stage_state.defender_plan.values():

                space = new_game_state.map_state[battle_id[2]]
                for fac in space.forces:
                    for sec in space.forces[fac]:
                        for u in space.forces[fac][sec]:
                            tank_unit(new_game_state, fac, space, sec, u)

                tank_leader(new_game_state, battle_id[0], stage_state.attacker_plan["leader"])
                tank_leader(new_game_state, battle_id[1], stage_state.defender_plan["leader"])
                for leader in new_game_state.round_state.leaders_used:
                    space, sector = new_game_state.round_state.leaders_used[leader]
                    if space == battle_id[2]:
                        if leader != stage_state.attacker_plan["leader"]:
                            if leader != stage_state.defender_plan["leader"]:
                                faction = get_leader_faction(leader)
                                tank_leader(new_game_state, faction, leader)

                # Discard all treachery
                
                new_game_state.round_state.stage_state = battle.MainStage()
                return new_game_state

        # Check Attacker Leader (Add to leaders used if survives)

        # Check Defender Leader (Add to leaders used if survives)

        # Count Attacker Power

        # Count Defender Power

        # Determine Winner

        # Tank Loser Units (increase KH count if atreides)

        # Discard Loser Treachery

        # Pay Winner Spice for dead leaders

        # Winner Must Tank Units (increase KH count if atreides)
        # Winner Must decide whether to discard treachery

        new_game_state.round_state.stage_state.winner = None
        new_game_state.round_state.stage_state.substage_state = battle.WinnerSubStage()
        return new_game_state
