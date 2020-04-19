# StartNexus
# ProposeAlliance (alliances are consistent -->)
# ResolveAlliances
# Exit Nexus

from copy import deepcopy

from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.factions import FactionState
from dune.state.rounds import bidding
from dune.actions import args


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
        factions = [f for f in game_state.faction_state if f != faction]
        return args.MultiFaction(factions)

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

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state = bidding.BiddingRound()
        new_game_state.shai_hulud = None
        return new_game_state
