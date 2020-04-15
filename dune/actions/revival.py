from copy import deepcopy

from dune.actions import storm, args
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds.movement import MovementRound
from dune.state.leaders import parse_leader
from dune.actions.karama import discard_karama


def get_revivable_leaders(game_state, faction):
    leader_death_count = game_state.faction_state[faction].leader_death_count
    if len(leader_death_count) != 5:
        return []

    all_revivable_leaders = []

    if faction == "atreides":
        kwisatz_haderach_tanks = game_state.faction_state[faction].kwisatz_haderach_tanks
        if kwisatz_haderach_tanks is not None and kwisatz_haderach_tanks <= min(leader_death_count.values()):
            all_revivable_leaders.append(("Kwisatz-Haderach", 2))

    for leader in game_state.faction_state[faction].tank_leaders:
        if all([leader_death_count[leader[0]] <= leader_death_count[ldr] for ldr in leader_death_count]):
            all_revivable_leaders.append(leader)
    return all_revivable_leaders


class ProgressRevival(Action):
    name = "progress-revival"
    ck_round = "revival"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            if get_revivable_leaders(game_state, game_state.round_state.faction_turn):
                raise IllegalAction("They might want to revive that leader")

            if game_state.faction_state[game_state.round_state.faction_turn].tank_units:
                raise IllegalAction("They might want to revive those units")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for faction in storm.get_faction_order(game_state):
            if faction in game_state.round_state.factions_done:
                continue
            if game_state.faction_state[faction].tank_units:
                new_game_state.round_state.faction_turn = faction
                return new_game_state
            if get_revivable_leaders(game_state, faction):
                new_game_state.round_state.faction_turn = faction
                return new_game_state

        new_game_state.round_state = MovementRound()
        return new_game_state


def _parse_revival_units(args):
    if not args:
        return []

    units = []
    for i in args.split(","):
        if i in ["1", "2"]:
            units.append(int(i))
        else:
            raise BadCommand("What sort of unit is _that_?")
    return units


def _parse_revival_leader(args):
    if (args == "") or (args == "-"):
        return None
    if args == "Kwisatz-Haderach":
        return ("Kwisatz-Haderach", 2)
    else:
        return parse_leader(args)


def _get_leader_cost(leader):
    return leader[1] if leader else 0


def _get_unit_cost(faction, units):
    cost = len(units) * 2
    if faction in ["emperor", "bene-gesserit", "guild"]:
        cost = max(0, cost - 2)
    if faction in ["atreides", "harkonnen"]:
        cost = max(0, cost - 4)
    if faction == "fremen":
        cost = 0
    return cost


def _execute_revival(units, leader, faction, game_state, cost):
    if len(units) > 3:
        raise BadCommand("You can only revive up to three units")
    if units.count("2") > 1:
        raise BadCommand("Only 1 Sardukar or Fedykin can be be revived per turn")
    new_game_state = deepcopy(game_state)
    for u in units:
        if u not in new_game_state.faction_state[faction].tank_units:
            raise BadCommand("Those units are not in the tanks")
        new_game_state.faction_state[faction].tank_units.remove(u)
        new_game_state.faction_state[faction].reserve_units.append(u)


    if cost > new_game_state.faction_state[faction].spice:
        raise BadCommand("You do not have the spice to perform this revival")
    new_game_state.faction_state[faction].spice -= cost

    if leader is not None:
        if leader[0] == "Kwisatz-Haderach":
            new_game_state.faction_state[faction].kwisatz_haderach_tanks = None
        else:
            new_game_state.faction_state[faction].tank_leaders.remove(leader)
            new_game_state.faction_state[faction].leaders.append(leader)

    return new_game_state


class KaramaFreeUnitRevival(Action):
    name = "karama-free-unit-revival"
    ck_karama = True

    def __init__(self, faction, units):
        self.faction = faction
        self.units = units

    @classmethod
    def _check(cls, game_state, faction):
        if faction != "emperor":
            raise IllegalAction("Only the emperor can revive units for free")
        if not game_state.faction_state[faction].tank_units:
            raise IllegalAction("You don't have any units to revive")

    @classmethod
    def parse_args(cls, faction, args):
        units = _parse_revival_units(args)
        if not units:
            raise IllegalAction("Can't revive no units")
        return KaramaFreeUnitRevival(faction, units)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.RevivalUnits(game_state.faction_state[faction].tank_units)

    def _execute(self, game_state):
        new_game_state = _execute_revival(self.units,
                                          None,
                                          self.faction,
                                          game_state,
                                          0)
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaFreeLeaderRevival(Action):
    name = "karama-free-leader-revival"
    ck_karama = True

    def __init__(self, faction, leader):
        self.faction = faction
        self.leader = leader

    @classmethod
    def _check(cls, game_state, faction):
        if faction != "emperor":
            raise IllegalAction("Only the emperor can revive leaders for free")
        if not game_state.faction_state[faction].tank_leaders:
            raise IllegalAction("You don't have any leaders to revive")

    @classmethod
    def parse_args(cls, faction, args):
        return KaramaFreeLeaderRevival(faction, parse_leader(args))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.RevivalLeader(game_state.faction_state[faction].tank_leaders,
                                  required=True)

    def _execute(self, game_state):
        new_game_state = _execute_revival([],
                                          self.leader,
                                          self.faction,
                                          game_state,
                                          0)
        discard_karama(new_game_state, self.faction)
        return new_game_state


class Revive(Action):
    name = "revive"
    ck_round = "revival"

    @classmethod
    def parse_args(cls, faction, args):
        if not args:
            return Revive(faction, [], None)
        units, leader = args.split(" ")
        return Revive(faction, _parse_revival_units(units), _parse_revival_leader(leader))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(
            args.RevivalUnits(game_state.faction_state[faction].tank_units),
            args.RevivalLeader(get_revivable_leaders(game_state, faction))
        )

    def __init__(self, faction, units, leader):
        self.faction = faction
        self.units = units
        self.leader = leader

    @classmethod
    def _check(cls, game_state, faction):
        if (not game_state.faction_state[faction].tank_units) and \
           get_revivable_leaders(game_state, faction):
            raise IllegalAction("You don't have anything to revive")
        Action.check_turn(game_state, faction)

    def _execute(self, game_state):
        if self.leader and self.leader not in get_revivable_leaders(game_state, self.faction):
            raise BadCommand("That leader is not revivable")

        new_game_state = _execute_revival(self.units,
                                self.leader,
                                self.faction,
                                game_state,
                                _get_unit_cost(self.faction, self.units) + _get_leader_cost(self.leader))
        faction_order = storm.get_faction_order(game_state)
        index = faction_order.index(self.faction) + 1
        if index < len(faction_order):
            new_game_state.round_state.factions_done.append(self.faction)
            new_game_state.round_state.faction_turn = faction_order[index]
        else:
            new_game_state.round_state = MovementRound()
        return new_game_state

