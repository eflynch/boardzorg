from copy import deepcopy

from dune.actions import storm, args
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds.movement import MovementRound
from dune.state.leaders import parse_leader


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
            return all_revivable_leaders.append(leader)

    return all_revivable_leaders


class ProgressRevival(Action):
    name = "progress-revival"
    ck_round = "revival"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            if len(get_revivable_leaders(game_state, game_state.round_state.faction_turn)) > 0:
                raise IllegalAction("They might want to revive that leader")

            if game_state.faction_state[game_state.round_state.faction_turn].tank_units:
                raise IllegalAction("They might want to revive those units")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for faction in storm.get_faction_order(game_state):
            if game_state.faction_state[faction].tank_units:
                new_game_state.round_state.faction_turn = faction
                return new_game_state
            if len(get_revivable_leaders(game_state, faction)) > 0:
                new_game_state.round_state.faction_turn = faction
                return new_game_state

        new_game_state.round_state = MovementRound()
        return new_game_state


class Revive(Action):
    name = "revive"
    ck_round = "revival"

    @classmethod
    def parse_args(cls, faction, args):
        if not args:
            return Revive(faction, [], None)
        units = []
        leader = None
        for i in args.split(","):
            if i in ["1", "2"]:
                units.append(int(i))
            else:
                if leader is not None:
                    raise BadCommand("Only one leader can be revived per turn")
                leader = i
        if leader is not None:
            if leader == "Kwisatz-Haderach":
                leader = ("Kwisatz-Haderach", 2)
            else:
                leader = parse_leader(leader)
        return Revive(faction, units, leader)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        leaders = get_revivable_leaders(game_state, faction)
        units = game_state.faction_state[faction].tank_units
        return args.Revival(leaders=leaders, units=units)

    def __init__(self, faction, units, leader):
        self.faction = faction
        self.units = units
        self.leader = leader

    @classmethod
    def _check(cls, game_state, faction):
        if (not game_state.faction_state[faction].tank_units) and \
           len(get_revivable_leaders(game_state, faction)) == 0:
            raise IllegalAction("You don't have anything to revive")
        cls.check_turn(game_state, faction)

    def _execute(self, game_state):
        if len(self.units) > 3:
            raise BadCommand("You can only revive up to three units")
        if self.units.count("2") > 1:
            raise BadCommand("Only 1 Sardukar or Fedykin can be be revived per turn")
        new_game_state = deepcopy(game_state)
        for u in self.units:
            if u not in new_game_state.faction_state[self.faction].tank_units:
                raise BadCommand("Those units are not in the tanks")
            new_game_state.faction_state[self.faction].tank_units.remove(u)
            new_game_state.faction_state[self.faction].reserve_units.append(u)

        cost = len(self.units) * 2
        if self.faction in ["emperor", "bene-gesserit", "guild"]:
            cost = max(0, cost - 2)
        if self.faction in ["atreides", "harkonnen"]:
            cost = max(0, cost - 4)
        if self.faction == "fremen":
            cost = 0

        if self.leader:
            cost += self.leader[1]

        if cost > new_game_state.faction_state[self.faction].spice:
            raise BadCommand("You do not have the spice to perform this revival")
        new_game_state.faction_state[self.faction].spice -= cost

        if self.leader is not None:
            if self.leader not in get_revivable_leaders(game_state, self.faction):
                raise BadCommand("That leader is not revivable")

            if self.leader[0] == "Kwisatz-Haderach":
                new_game_state.faction_state[self.faction].kwisatz_haderach_tanks = None
            else:
                new_game_state.faction_state[self.faction].tank_leaders.remove(self.leader)
                new_game_state.faction_state[self.faction].leaders.append(self.leader)

        faction_order = storm.get_faction_order(game_state)
        index = faction_order.index(self.faction) + 1
        if index < len(faction_order):
            new_game_state.round_state.faction_turn = faction_order[index]
        else:
            new_game_state.round_state = MovementRound()

        return new_game_state
