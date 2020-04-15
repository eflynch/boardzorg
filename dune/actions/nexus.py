# StartNexus
# ProposeAlliance (alliances are consistent -->)
# ResolveAlliances
# KaramaWormRide, KaramaPass -->
# WormRide, WormRidePass -->
# Exit Nexus

from copy import deepcopy

from dune.actions.action import Action
from dune.actions.movement import move_units
from dune.exceptions import IllegalAction, BadCommand
from dune.state.factions import FactionState
from dune.actions import args
from dune.actions.karama import discard_karama


def fremen_allies_present(game_state):
    allies = set(["fremen"]) | game_state.alliances["fremen"]
    for a in allies:
        if a in game_state.map_state[game_state.shai_hulud].forces:
            return True
    return False


def all_disjoint(sets):
    all = set()
    for s in sets:
        for x in s:
            if x in all:
                return False
            all.add(x)
    return True


def alliances_work(game_state):
    sets = []
    for f in game_state.alliances:
        if f not in game_state.round_state.proposals:
            return False
        sets.append(frozenset(game_state.round_state.proposals[f] | set([f])))

    if not all_disjoint(set(sets)):
        return False

    return True


class KaramaWormRide(Action):
    name = "karama-worm-ride"
    ck_round = "nexus"
    ck_karama = True

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if not fremen_allies_present(game_state):
            raise IllegalAction("No worm ride to karama")

        if game_state.round_state.worm_done:
            raise IllegalAction("Karama already used or passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.worm_done = True
        discard_karama(new_game_state, self.faction)

        return new_game_state


class KaramaPassWormRide(Action):
    name = "karam-pass-worm-ride"
    ck_round = "nexus"

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "fremen":
            raise IllegalAction("You can't karama your own desert powers")
        if game_state.round_state.karama_done:
            raise IllegalAction("Karama already used or passed")

        if faction in game_state.round_state.karama_passes:
            raise IllegalAction("You already passed karama")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.karama_passes.append(self.faction)
        return new_game_state


class ProposeAlliance(Action):
    name = "propose"
    ck_round = "nexus"

    @classmethod
    def parse_args(cls, faction, args):
        if args:
            factions = args.split(" ")
        else:
            factions = []

        if faction in factions:
            raise BadCommand("Don't include yourself in your proposed alliance")

        for f in factions:
            if f not in FactionState.ALL_FACTIONS:
                raise BadCommand("That faction is not in the game")

        return ProposeAlliance(faction, factions)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.MultiFaction()

    def __init__(self, faction, factions):
        self.faction = faction
        self.factions = factions

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.proposals_done:
            raise IllegalAction("Alliances are already resolved")

    def _execute(self, game_state):
        factions = set(self.factions)
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.proposals[self.faction] = factions
        return new_game_state


class ResolveAlliance(Action):
    name = "resolve-alliances"
    ck_round = "nexus"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not alliances_work(game_state):
            raise IllegalAction("Alliances are not done")
        if game_state.round_state.proposals_done:
            raise IllegalAction("Alliances already resolved")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.alliances = new_game_state.round_state.proposals
        new_game_state.round_state.proposals_done = True
        return new_game_state


class EndNexus(Action):
    name = "end-nexus"
    ck_round = "nexus"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.round_state.proposals_done:
            raise IllegalAction("Waiting for alliances to resolve")
        if fremen_allies_present(game_state) and not game_state.round_state.worm_done:
            raise IllegalAction("Waiting for the worm")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space = new_game_state.map_state[new_game_state.shai_hulud]
        factions = list(space.forces.keys())
        for faction in factions:
            if faction != "fremen":
                del space.forces[faction]
        space.spice = 0
        space.coexist = False
        new_game_state.shai_hulud = None
        new_game_state.round = "spice"
        return new_game_state


class WormRide(Action):
    name = "ride"
    ck_round = "nexus"

    @classmethod
    def parse_args(cls, faction, args):
        space, sector = args.split(" ")
        sector = int(sector)
        return WormRide(faction, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.SpaceSector()

    def __init__(self, faction, space, sector):
        self.faction = faction
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        cls.check_alliance(game_state, faction, "fremen")
        space = game_state.map_state[game_state.shai_hulud]
        if faction not in space.forces:
            raise IllegalAction("You need worm riders to ride a worm")

        if len(game_state.round_state.karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Karama will be used")

        if game_state.round_state.worm_done:
            raise IllegalAction("No more worm riding for you today")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space = new_game_state.map_state[new_game_state.shai_hulud]
        new_space = new_game_state.map_state[self.space]

        for s in space.forces[self.faction]:
            units = space.forces[self.faction][s][:]
            move_units(new_game_state, self.faction, units, space, s, new_space, self.sector)

        new_game_state.round_state.worm_done = True

        return new_game_state
