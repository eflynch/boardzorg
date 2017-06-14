from dune.actions import storm
from dune.exceptions import BadCommand
from dune.map.map import MapGraph
from dune.state.leaders import parse_leader
from dune.state.treachery_cards import WEAPONS, DEFENSES, WORTHLESS
from dune.state.treachery_cards import PROJECTILE_WEAPONS, POISON_WEAPONS, PROJECTILE_DEFENSES, POISON_DEFENSES


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


def discard_treachery(game_state, card):
    if card is not None:
        game_state.treachery_discard.insert(0, card)


def clash_weapons(attack, defense):
    if attack == "Lasgun":
        return True
    if attack in POISON_WEAPONS:
        return defense not in POISON_DEFENSES
    if attack in PROJECTILE_WEAPONS:
        return defense not in PROJECTILE_DEFENSES
    return False


def count_power(space, faction_a, faction_b, sectors, karama_fedaykin, karama_sardaukar):
    if faction_a == "fremen" and karama_fedaykin:
        def unit_power(u): return 1
    elif faction_a == "emperor" and karama_sardaukar:
        def unit_power(u): return 1
    elif faction_a == "emperor" and faction_b == "fremen":
        def unit_power(u): return 1
    else:
        def unit_power(u): return u

    return sum(sum(unit_power(u) for u in space.forces[faction_a][s]) for s in sectors)
