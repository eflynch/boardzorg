from copy import deepcopy

from dune.actions import storm
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds.movement import MovementRound
from dune.state.leaders import parse_leader


def leader_revivable(game_state, faction):
    leader_death_count = game_state.faction_state[faction].leader_death_count
    if len(leader_death_count) != 5:
        return False

    if not game_state.faction_state[faction].tank_leaders:
        return False
    for leader in game_state.faction_state[faction].tank_leaders:
        if all([leader_death_count[leader[0]] <= leader_death_count[ldr] for ldr in leader_death_count]):
            return True
    return False


class StartRevival(Action):
    name = "start-revival"
    ck_round = "revival"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            raise IllegalAction("Revival already begun")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for faction in storm.get_faction_order(game_state):
            if game_state.faction_state[faction].tank_units:
                new_game_state.round_state.faction_turn = faction
                return new_game_state
            if leader_revivable(game_state, faction):
                new_game_state.round_state.faction_turn = faction
                return new_game_state

        new_game_state.round_state = MovementRound()
        return new_game_state


class Revive(Action):
    name = "revive"
    ck_round = "revival"

    @classmethod
    def parse_args(cls, faction, args):
        units = []
        leader = None
        for i in args.split(","):
            if i in ["1", "2"]:
                units.append(int(i))
            else:
                leader = i
        if leader is not None:
            leader = parse_leader(leader)
        return Revive(faction, units, leader)

    def __init__(self, faction, units, leader):
        self.faction = faction
        self.units = units
        self.leader = leader

    @classmethod
    def _check(cls, game_state, faction):
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

        if cost > new_game_state.faction_state[self.faction].spice:
            raise BadCommand("You do not have the spice to revive those units")
        new_game_state.faction_state[self.faction].spice -= cost

        if self.leader is not None:
            if self.leader not in new_game_state.faction_state[self.faction].tank_leaders:
                raise BadCommand("That leader is not in the tanks")
            leader_death_count = new_game_state.faction_state[self.faction].leader_death_count
            if len(leader_death_count) != 5:
                raise BadCommand("You cannot revive leaders until they all die")

            for ldr in leader_death_count:
                if leader_death_count[self.leader[0]] > leader_death_count[ldr]:
                    raise BadCommand("You cannot revive a leader again until all others have died")

            new_game_state.faction_state[self.faction].tank_leaders.remove(self.leader)
            new_game_state.faction_state[self.faction].leaders.append(self.leader)

        faction_order = storm.get_faction_order(game_state)
        index = faction_order.index(self.faction) + 1
        if index < len(faction_order):
            new_game_state.round_state.faction_turn = faction_order[index]
        else:
            new_game_state.round_state = MovementRound()

        return new_game_state
