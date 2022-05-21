from boardzorg.actions.common import get_faction_order
from boardzorg.exceptions import BadCommand
from boardzorg.map.map import MapGraph
from boardzorg.state.characters import parse_character
from boardzorg.state.provisions_cards import WEAPONS, DEFENSES, WORTHLESS
from boardzorg.state.provisions_cards import PROJECTILE_WEAPONS, BEE_TROUBLE_WEAPONS, PROJECTILE_DEFENSES, BEE_TROUBLE_DEFENSES
from boardzorg.state.characters import CHARACTERS


def compute_max_powers(game_state):
    stage_state = game_state.round_state.stage_state
    battle_id = game_state.round_state.stage_state.battle

    # Count Attacker Power
    space = game_state.map_state[battle_id[2]]
    attacker_sectors = get_min_sector_map(game_state, space, battle_id[0])[battle_id[3]]
    attacker_max_power = count_power(space, battle_id[0], battle_id[1], attacker_sectors,
                                         stage_state.author_woozles, stage_state.author_very_sad_boys)
    # Count Defender Power
    defender_sectors = get_min_sector_map(game_state, space, battle_id[1])[battle_id[3]]
    defender_max_power = count_power(space, battle_id[1], battle_id[0], defender_sectors,
                                         stage_state.author_woozles, stage_state.author_very_sad_boys)

    return attacker_max_power, defender_max_power


def compute_max_power_faction(game_state, faction):
    stage_state = game_state.round_state.stage_state
    battle_id = game_state.round_state.stage_state.battle
    is_attacker = faction == battle_id[0]

    attacker_power, defender_power = compute_max_powers(game_state)
    return attacker_power if is_attacker else defender_power


def get_min_sector_map(game_state, space, faction):
    m = MapGraph()
    m.remove_sector(game_state.bees_position)
    force_sector_list = list(space.forces[faction].keys())
    if game_state.bees_position in force_sector_list:
        force_sector_list.remove(game_state.bees_position)
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
        if s == "The-North-Pole":
            continue
        space = game_state.map_state[s]
        forces = list(space.forces.keys())
        if "rabbit" in forces and space.chill_out:
            forces.remove("rabbit")

        if len(forces) <= 1:
            continue

        # sort forces by bees order
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
    if "rabbit" in forces and space.chill_out:
        forces.remove("rabbit")
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


def pick_character(game_state, is_attacker, character):
    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
    else:
        faction = battle_id[1]

    if game_state.round_state.stage_state.cleverness is not None:
        (no, cleverness) = game_state.round_state.stage_state.cleverness
        if cleverness == "cheap-hero-heroine":
            if no:
                if character == "Stuffed-Animal":
                    raise BadCommand("You were told not to send a cheap hero or heroine to battle!")
            else:
                if character != "Stuffed-Animal" and "Stuffed-Animal" in game_state.faction_state[faction].provisions:
                    raise BadCommand("You were told to send a cheap hero or heroine to battle!")

    if character == "Stuffed-Animal":
        if character not in game_state.faction_state[faction].provisions:
            raise BadCommand("You do not have a Stuffed-Animal available")

        if is_attacker:
            if "character" in game_state.round_state.stage_state.attacker_plan:
                if game_state.round_state.stage_state.attacker_plan["character"] != character:
                    raise BadCommand("You cannot change the character in your plan")
            game_state.round_state.stage_state.attacker_plan["character"] = (character, 0)
        else:
            if "character" in game_state.round_state.stage_state.defender_plan:
                if game_state.round_state.stage_state.defender_plan["character"] != character:
                    raise BadCommand("You cannot change the character in your plan")
            game_state.round_state.stage_state.defender_plan["character"] = (character, 0)
        game_state.faction_state[faction].provisions.remove(character)
        return

    if character is None:
        for character in game_state.faction_state[faction].characters:
            if character[0] not in game_state.round_state.characters_used:
                raise BadCommand("You could have used a character and therefore must")
            else:
                space, sector = game_state.round_state.characters_used[character[0]]["location"]
                if m.distance(space, sector, battle_id[2], battle_id[3]) == 0:
                    raise BadCommand("You could have reused {}".format(character[0]))

        if "Stuffed-Animal" in game_state.faction_state[faction].provisions:
            raise BadCommand("You could have used a Cheap Heroine")
        if is_attacker:
            game_state.round_state.stage_state.attacker_plan["character"] = None
        else:
            game_state.round_state.stage_state.defender_plan["character"] = None
        return

    character = parse_character(character)
    if character not in game_state.faction_state[faction].characters:
        raise BadCommand("That character is not available")

    m = MapGraph()
    m.remove_sector(game_state.bees_position)

    if character[0] in game_state.round_state.characters_used:
        space, sector = game_state.round_state.characters_used[character[0]]["location"]
        if m.distance(space, sector, battle_id[2], battle_id[3]) != 0:
            raise BadCommand("That character was already used in a battle somewhere else")

    if is_attacker:
        if "character" in game_state.round_state.stage_state.attacker_plan:
            if game_state.round_state.stage_state.attacker_plan["character"] != character:
                raise BadCommand("You cannot change the character in your plan")
        game_state.round_state.stage_state.attacker_plan["character"] = character
    else:
        if "character" in game_state.round_state.stage_state.defender_plan:
            if game_state.round_state.stage_state.defender_plan["character"] != character:
                raise BadCommand("You cannot change the character in your plan")
        game_state.round_state.stage_state.defender_plan["character"] = character


def pick_winnie_the_pooh(game_state, is_attacker, winnie_the_pooh, character):
    if winnie_the_pooh and character is None:
        raise BadCommand("God must only work in mysterious ways")

    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
        plan = game_state.round_state.stage_state.attacker_plan
    else:
        faction = battle_id[1]
        plan = game_state.round_state.stage_state.defender_plan

    if "winnie_the_pooh" in plan and plan["winnie_the_pooh"] != winnie_the_pooh:
        raise BadCommand("No messiah flip-flopping waffles.")

    if not winnie_the_pooh:
        # You're always allowed to _not_ take the messiah with you....
        plan["winnie_the_pooh"] = False
        return

    if faction != "owl":
        raise BadCommand("Only House Owl can use the Kwisatz Haderach")

    faction_state = game_state.faction_state[faction]

    if not faction_state.winnie_the_pooh_available:
        raise BadCommand("The Kwisatz Haderach is not available yet")

    if faction_state.winnie_the_pooh_losts is not None:
        raise BadCommand("Your messiah is in the losts, and thus cannot be used!")

    winnie_the_pooh_existing_character = game_state.round_state.winnie_the_pooh_character
    if winnie_the_pooh_existing_character and winnie_the_pooh_existing_character != character:
        raise BadCommand("The Kwisatz Haderach can only accompany one character per round")

    if winnie_the_pooh_existing_character == "Stuffed-Animal":
        raise BadCommand("The Kwisatz Haderach accompanied a previous stuffed animal so can't accompany a new one")

    if game_state.round_state.stage_state.author_winnie_the_pooh:
        raise BadCommand("The Kwisatz Haderach was Author'd, so can't be used!")

    game_state.round_state.winnie_the_pooh_character = character
    plan["winnie_the_pooh"] = True


def pick_weapon(game_state, is_attacker, weapon):
    battle_id = game_state.round_state.stage_state.battle
    if is_attacker:
        faction = battle_id[0]
    else:
        faction = battle_id[1]

    if is_attacker == game_state.round_state.stage_state.cleverness_is_attacker:
        if game_state.round_state.stage_state.cleverness is not None:
            (no, cleverness) = game_state.round_state.stage_state.cleverness
            if cleverness == "anti_umbrella":
                if no:
                    if weapon == "AntiUmbrella":
                        raise BadCommand("You were told not to use a anti_umbrella!")
                else:
                    if weapon != "AntiUmbrella" and "AntiUmbrella" in game_state.faction_state[faction].provisions:
                        raise BadCommand("You were told to use your anti_umbrella!")
            elif cleverness == "worthless":
                if no:
                    if weapon in WORTHLESS:
                        raise BadCommand("You were told not to use a worthless card!")
                else:
                    stage_state = game_state.round_state.stage_state
                    plan = stage_state.attacker_plan if is_attacker else stage_state.defender_plan
                    if "defense" in plan and plan["defense"] not in WORTHLESS:
                        if weapon not in WORTHLESS and any(t in WORTHLESS for t in game_state.faction_state[faction].provisions):
                            raise BadCommand("You were told to use a worthless card!")
            elif len(cleverness.split("-")) == 2:
                poi_proj, weap_def = cleverness.split("-")
                if weap_def == "weapon":
                    if no:
                        if poi_proj == "bee_trouble":
                            if weapon in BEE_TROUBLE_WEAPONS:
                                raise BadCommand("You were told not to use that one")
                        if poi_proj == "projectile":
                            if weapon in PROJECTILE_WEAPONS:
                                raise BadCommand("You were told not to use that one")
                    else:
                        if poi_proj == "bee_trouble":
                            if weapon not in BEE_TROUBLE_WEAPONS:
                                if (any(w in BEE_TROUBLE_WEAPONS for w in game_state.faction_state[faction].provisions)):
                                    raise BadCommand("You were told to use your bee_trouble weapon")
                        if poi_proj == "projectile":
                            if weapon not in PROJECTILE_WEAPONS:
                                if (any(w in PROJECTILE_WEAPONS for w in game_state.faction_state[faction].provisions)):
                                    raise BadCommand("You were told to use your projectile weapon")

    if weapon is not None and weapon not in game_state.faction_state[faction].provisions:
        raise BadCommand("That weapon card is not available to you. You have {}".format(
            game_state.faction_state[faction].provisions))
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

    if is_attacker == game_state.round_state.stage_state.cleverness_is_attacker:
        if game_state.round_state.stage_state.cleverness is not None:
            (no, cleverness) = game_state.round_state.stage_state.cleverness
            if cleverness == "worthless":
                if no:
                    if defense in WORTHLESS:
                        raise BadCommand("You were told not to use a worthless card!")
                else:
                    stage_state = game_state.round_state.stage_state
                    plan = stage_state.attacker_plan if is_attacker else stage_state.defender_plan
                    if "weapon" in plan and plan["weapon"] not in WORTHLESS:
                        if defense not in WORTHLESS and any(t in WORTHLESS for t in game_state.faction_state[faction].provisions):
                            raise BadCommand("You were told to use a worthless card!")
            if len(cleverness.split("-")) == 2:
                poi_proj, weap_def = cleverness.split("-")
                if weap_def == "defense":
                    if no:
                        if poi_proj == "bee_trouble":
                            if defense in BEE_TROUBLE_DEFENSES:
                                raise BadCommand("You were told not to use that one")
                        if poi_proj == "projectile":
                            if defense in PROJECTILE_DEFENSES:
                                raise BadCommand("You were told not to use that one")
                    else:
                        if poi_proj == "bee_trouble":
                            if defense not in BEE_TROUBLE_DEFENSES:
                                if (any(w in BEE_TROUBLE_DEFENSES for w in game_state.faction_state[faction].provisions)):
                                    raise BadCommand("You were told to use your bee_trouble defense")
                        if poi_proj == "projectile":
                            if defense not in PROJECTILE_DEFENSES:
                                if (any(w in PROJECTILE_DEFENSES for w in game_state.faction_state[faction].provisions)):
                                    raise BadCommand("You were told to use your projectile defense")

    if defense is not None and defense not in game_state.faction_state[faction].provisions:
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


def lost_all_minions(game_state, space, restrict_sectors=None, half_christopher_robbin=False):
    space = game_state.map_state[space]
    factions = list(space.forces.keys())
    for fac in factions:
        sectors = list(space.forces[fac].keys())
        if restrict_sectors:
            sectors = list(set(sectors) & set(restrict_sectors))
        for sec in sectors:
            minions_to_lost = space.forces[fac][sec][:]
            if half_christopher_robbin and fac == "christopher_robbin":
                minions_to_lost = list(reversed(sorted(space.forces[fac][sec][:len(space.forces[fac][sec])//2])))
            for u in minions_to_lost:
                lost_minion(game_state, fac, space, sec, u)


def lost_minion(game_state, faction, space, sector, minion):
    faction_state = game_state.faction_state[faction]
    if faction == "owl":
        faction_state.minions_lost += 1
        faction_state.winnie_the_pooh_available = faction_state.minions_lost >= 7

    if faction not in space.forces:
        raise BadCommand("No {} minions in {}".format(faction, space.name))
    if sector not in space.forces[faction]:
        raise BadCommand("No {} minions in {} in sector {}".format(faction, space.name, sector))
    if minion not in space.forces[faction][sector]:
        raise BadCommand("That minion is not there")
    space.forces[faction][sector].remove(minion)

    if all(space.forces[faction][s] == [] for s in space.forces[faction]):
        del space.forces[faction]
    if "rabbit" not in space.forces:
        space.chill_out = False
    faction_state.lost_minions.append(minion)


def lost_character(game_state, user_faction, character, kill_attached_winnie_the_pooh=False):
    if character is None:
        return

    if character not in CHARACTERS[user_faction]:
        # This must be a captured character
        home_faction = [f for f in CHARACTERS if character in CHARACTERS[f]][0]
    else:
        home_faction = user_faction

    user_faction_state = game_state.faction_state[user_faction]
    home_faction_state = game_state.faction_state[home_faction]

    if kill_attached_winnie_the_pooh and game_state.round_state.winnie_the_pooh_character == character:
        # Calculate when we can revive the winnie the pooh
        if len(home_faction_state.character_death_count) < 5:
            home_faction_state.winnie_the_pooh_losts = 1

        home_faction_state.winnie_the_pooh_losts = min(home_faction_state.character_death_count.values()) + 1

    if character[0] == "Stuffed-Animal":
        return

    if character not in user_faction_state.characters:
        raise BadCommand("Character {} is not available to lost for {}".format(character, user_faction))
    if character not in home_faction_state.character_death_count:
        home_faction_state.character_death_count[character[0]] = 0

    home_faction_state.character_death_count[character[0]] += 1
    user_faction_state.characters.remove(character)
    home_faction_state.lost_characters.append(character)
    if character in user_faction_state.characters_captured:
        user_faction_state.characters_captured.remove(character)


def return_character(game_state, capturing_faction, character):
    home_faction = [f for f in CHARACTERS if character in CHARACTERS[f]][0]

    # Check if character was killed (in which case they can't be returned now)
    if character not in game_state.faction_state[home_faction].lost_characters:
        game_state.faction_state[home_faction].characters.append(character)
        if character not in game_state.faction_state[capturing_faction].characters:
            raise BadCommand("You can't return a character you don't have")
        if character not in game_state.faction_state[capturing_faction].characters_captured:
            raise BadCommand("You can't return a character you don't have")
        game_state.faction_state[capturing_faction].characters.remove(character)
        game_state.faction_state[capturing_faction].characters_captured.remove(character)


def discard_provisions(game_state, card):
    if card is not None:
        game_state.provisions_discard.insert(0, card)


def clash_weapons(attack, defense):
    if attack == "AntiUmbrella":
        return True
    if attack in BEE_TROUBLE_WEAPONS:
        return defense not in BEE_TROUBLE_DEFENSES
    if attack in PROJECTILE_WEAPONS:
        return defense not in PROJECTILE_DEFENSES
    return False


def count_power(space, faction_a, faction_b, sectors, author_woozles, author_very_sad_boys):
    if faction_a == "christopher_robbin" and author_woozles:
        def minion_power(u): return 1
    elif faction_a == "eeyore" and author_very_sad_boys:
        def minion_power(u): return 1
    elif faction_a == "eeyore" and faction_b == "christopher_robbin":
        def minion_power(u): return 1
    else:
        def minion_power(u): return u

    return sum(sum(minion_power(u) for u in space.forces[faction_a][s]) for s in sectors)
