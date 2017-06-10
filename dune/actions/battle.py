from copy import deepcopy

from dune.actions.action import Action
from dune.actions import storm
from dune.state.rounds import battle, collection
from dune.exceptions import IllegalAction, BadCommand
from dune.map.map import MapGraph


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
