from dune.actions.common import get_faction_order
from dune.exceptions import BadCommand
from dune.map.map import MapGraph
from dune.state.leaders import parse_leader
from dune.state.treachery_cards import WEAPONS, DEFENSES, WORTHLESS
from dune.state.treachery_cards import PROJECTILE_WEAPONS, POISON_WEAPONS, PROJECTILE_DEFENSES, POISON_DEFENSES
from dune.state.leaders import LEADERS


def compute_max_powers(game_state):
    stage_state = game_state.round_state.stage_state
    battle_id = game_state.round_state.stage_state.battle

    # Count Attacker Power
    space = game_state.map_state[battle_id[2]]
    attacker_sectors = get_min_sector_map(game_state, space, battle_id[0])[battle_id[3]]
    attacker_max_power = count_power(space, battle_id[0], battle_id[1], attacker_sectors,
                                         stage_state.karama_fedaykin, stage_state.karama_sardaukar)
    # Count Defender Power
    defender_sectors = get_min_sector_map(game_state, space, battle_id[1])[battle_id[3]]
    defender_max_power = count_power(space, battle_id[1], battle_id[0], defender_sectors,
                                         stage_state.karama_fedaykin, stage_state.karama_sardaukar)

    return attacker_max_power, defender_max_power


def compute_max_power_faction(game_state, faction):
    stage_state = game_state.round_state.stage_state
    battle_id = game_state.round_state.stage_state.battle
    is_attacker = faction == battle_id[0]

    attacker_power, defender_power = compute_max_powers(game_state)
    return attacker_power if is_attacker else defender_power


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
            if m.distance(space.name, msec, space.name, s) == 0:
                if msec not in min_sectors:
                    min_sectors[msec] = []
                min_sectors[msec].append(s)
                break
    return min_sectors


def find_battles(game_state):
    faction_order = get_faction_order(game_state)
    battles = []

    for s in game_state.map_state:
        if s == "Polar-Sink":
            continue
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
                    for f_msec in g_map:
                        if (g, f, s, f_msec) not in battles:
                            battles.append((f, g, s, f_msec))
    battles.sort(key=lambda b: faction_order.index(b[0]))
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

    if game_state.round_state.stage_state.voice is not None:
        (no, voice) = game_state.round_state.stage_state.voice
        if voice == "cheap-hero-heroine":
            if no:
                if leader == "Cheap-Hero/Heroine":
                    raise BadCommand("You were told not to send a cheap hero or heroine to battle!")
            else:
                if leader != "Cheap-Hero/Heroine" and "Cheap-Hero/Heroine" in game_state.faction_state[faction].treachery:
                    raise BadCommand("You were told to send a cheap hero or heroine to battle!")

    if leader == "Cheap-Hero/Heroine":
        if leader not in game_state.faction_state[faction].treachery:
            raise BadCommand("You do not have a Cheap-Hero/Heroine available")

        if is_attacker:
            if "leader" in game_state.round_state.stage_state.attacker_plan:
                if game_state.round_state.stage_state.attacker_plan["leader"] != leader:
                    raise BadCommand("You cannot change the leader in your plan")
            game_state.round_state.stage_state.attacker_plan["leader"] = (leader, 0)
        else:
            if "leader" in game_state.round_state.stage_state.defender_plan:
                if game_state.round_state.stage_state.defender_plan["leader"] != leader:
                    raise BadCommand("You cannot change the leader in your plan")
            game_state.round_state.stage_state.defender_plan["leader"] = (leader, 0)
        game_state.faction_state[faction].treachery.remove(leader)
        return

    if leader is None:
        for leader in game_state.faction_state[faction].leaders:
            if leader[0] not in game_state.round_state.leaders_used:
                raise BadCommand("You could have used a leader and therefore must")
            else:
                space, sector = game_state.round_state.leaders_used[leader[0]]["location"]
                if m.distance(space, sector, battle_id[2], battle_id[3]) == 0:
                    raise BadCommand("You could have reused {}".format(leader[0]))

        if "Cheap-Hero/Heroine" in game_state.faction_state[faction].treachery:
            raise BadCommand("You could have used a Cheap Heroine")
        if is_attacker:
            game_state.round_state.stage_state.attacker_plan["leader"] = None
        else:
            game_state.round_state.stage_state.defender_plan["leader"] = None
        return

    leader = parse_leader(leader)
    if leader not in game_state.faction_state[faction].leaders:
        raise BadCommand("That leader is not available")

    m = MapGraph()
    m.remove_sector(game_state.storm_position)

    if leader[0] in game_state.round_state.leaders_used:
        space, sector = game_state.round_state.leaders_used[leader[0]]["location"]
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


def pick_kwisatz_haderach(game_state, is_attacker, kwisatz_haderach, leader):
    if kwisatz_haderach and leader is None:
        raise BadCommand("God must only work in mysterious ways")

    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
        plan = game_state.round_state.stage_state.attacker_plan
    else:
        faction = battle_id[1]
        plan = game_state.round_state.stage_state.defender_plan

    if "kwisatz_haderach" in plan and plan["kwisatz_haderach"] != kwisatz_haderach:
        raise BadCommand("No messiah flip-flopping waffles.")

    if not kwisatz_haderach:
        # You're always allowed to _not_ take the messiah with you....
        plan["kwisatz_haderach"] = False
        return

    if faction != "atreides":
        raise BadCommand("Only House Atreides can use the Kwisatz Haderach")

    faction_state = game_state.faction_state[faction]

    if not faction_state.kwisatz_haderach_available:
        raise BadCommand("The Kwisatz Haderach is not available yet")

    if faction_state.kwisatz_haderach_tanks is not None:
        raise BadCommand("Your messiah is in the tanks, and thus cannot be used!")

    kwisatz_haderach_existing_leader = game_state.round_state.kwisatz_haderach_leader
    if kwisatz_haderach_existing_leader and kwisatz_haderach_existing_leader != leader:
        raise BadCommand("The Kwisatz Haderach can only accompany one leader per round")

    if kwisatz_haderach_existing_leader == "Cheap-Hero/Heroine":
        raise BadCommand("The Kwisatz Haderach accompanied a previous cheap hero/heroine so can't accompany a new one")

    if game_state.round_state.stage_state.karama_kwisatz_haderach:
        raise BadCommand("The Kwisatz Haderach was Karama'd, so can't be used!")

    game_state.round_state.kwisatz_haderach_leader = leader
    plan["kwisatz_haderach"] = True


def pick_weapon(game_state, is_attacker, weapon):
    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
    else:
        faction = battle_id[1]

    if is_attacker == game_state.round_state.stage_state.voice_is_attacker:
        if game_state.round_state.stage_state.voice is not None:
            (no, voice) = game_state.round_state.stage_state.voice
            if voice == "lasgun":
                if no:
                    if weapon == "Lasgun":
                        raise BadCommand("You were told not to use a lasgun!")
                else:
                    if weapon != "Lasgun" and "Lasgun" in game_state.faction_state[faction].treachery:
                        raise BadCommand("You were told to use your lasgun!")
            elif voice == "worthless":
                if no:
                    if weapon in WORTHLESS:
                        raise BadCommand("You were told not to use a worthless card!")
                else:
                    stage_state = game_state.round_state.stage_state
                    plan = stage_state.attacker_plan if is_attacker else stage_state.defender_plan
                    if "defense" in plan and plan["defense"] not in WORTHLESS:
                        if weapon not in WORTHLESS and any(t in WORTHLESS for t in game_state.faction_state[faction].treachery):
                            raise BadCommand("You were told to use a worthless card!")
            elif len(voice.split("-")) == 2:
                poi_proj, weap_def = voice.split("-")
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
                                    raise BadCommand("You were told to use your projectile weapon")

    if weapon is not None and weapon not in game_state.faction_state[faction].treachery:
        raise BadCommand("That weapon card is not available to you. You have {}".format(
            game_state.faction_state[faction].treachery))
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


def pick_defense(game_state, is_attacker, defense):
    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
    else:
        faction = battle_id[1]

    if is_attacker == game_state.round_state.stage_state.voice_is_attacker:
        if game_state.round_state.stage_state.voice is not None:
            (no, voice) = game_state.round_state.stage_state.voice
            if voice == "worthless":
                if no:
                    if defense in WORTHLESS:
                        raise BadCommand("You were told not to use a worthless card!")
                else:
                    stage_state = game_state.round_state.stage_state
                    plan = stage_state.attacker_plan if is_attacker else stage_state.defender_plan
                    if "weapon" in plan and plan["weapon"] not in WORTHLESS:
                        if defense not in WORTHLESS and any(t in WORTHLESS for t in game_state.faction_state[faction].treachery):
                            raise BadCommand("You were told to use a worthless card!")
            if len(voice.split("-")) == 2:
                poi_proj, weap_def = voice.split("-")
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
                                    raise BadCommand("You were told to use your projectile defense")

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


def pick_number(game_state, max_power, is_attacker, number):
    if number > max_power or number < 0:
        raise BadCommand("Number must be between 0 and {}".format(max_power))
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


def tank_all_units(game_state, space, restrict_sectors=None, half_fremen=False):
    space = game_state.map_state[space]
    factions = list(space.forces.keys())
    for fac in factions:
        sectors = list(space.forces[fac].keys())
        if restrict_sectors:
            sectors = list(set(sectors) & set(restrict_sectors))
        for sec in sectors:
            units_to_tank = space.forces[fac][sec][:]
            if half_fremen and fac == "fremen":
                units_to_tank = list(reversed(sorted(space.forces[fac][sec][:len(space.forces[fac][sec])//2])))
            for u in units_to_tank:
                tank_unit(game_state, fac, space, sec, u)


def tank_unit(game_state, faction, space, sector, unit):
    faction_state = game_state.faction_state[faction]
    if faction == "atreides":
        faction_state.units_lost += 1
        faction_state.kwisatz_haderach_available = faction_state.units_lost >= 7

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


def tank_leader(game_state, user_faction, leader, kill_attached_kwisatz_haderach=False):
    if leader is None:
        return

    if leader not in LEADERS[user_faction]:
        # This must be a captured leader
        home_faction = [f for f in LEADERS if leader in LEADERS[f]][0]
    else:
        home_faction = user_faction

    user_faction_state = game_state.faction_state[user_faction]
    home_faction_state = game_state.faction_state[home_faction]

    if kill_attached_kwisatz_haderach and game_state.round_state.kwisatz_haderach_leader == leader:
        # Calculate when we can revive the kwisatz haderach
        if len(home_faction_state.leader_death_count) < 5:
            home_faction_state.kwisatz_haderach_tanks = 1

        home_faction_state.kwisatz_haderach_tanks = min(home_faction_state.leader_death_count.values()) + 1

    if leader[0] == "Cheap-Hero/Heroine":
        return

    if leader not in user_faction_state.leaders:
        raise BadCommand("Leader {} is not available to tank for {}".format(leader, user_faction))
    if leader not in home_faction_state.leader_death_count:
        home_faction_state.leader_death_count[leader[0]] = 0

    home_faction_state.leader_death_count[leader[0]] += 1
    user_faction_state.leaders.remove(leader)
    home_faction_state.tank_leaders.append(leader)
    if leader in user_faction_state.leaders_captured:
        user_faction_state.leaders_captured.remove(leader)


def return_leader(game_state, capturing_faction, leader):
    home_faction = [f for f in LEADERS if leader in LEADERS[f]][0]

    # Check if leader was killed (in which case they can't be returned now)
    if leader not in game_state.faction_state[home_faction].tank_leaders:
        game_state.faction_state[home_faction].leaders.append(leader)
        if leader not in game_state.faction_state[capturing_faction].leaders:
            raise BadCommand("You can't return a leader you don't have")
        if leader not in game_state.faction_state[capturing_faction].leaders_captured:
            raise BadCommand("You can't return a leader you don't have")
        game_state.faction_state[capturing_faction].leaders.remove(leader)
        game_state.faction_state[capturing_faction].leaders_captured.remove(leader)


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
