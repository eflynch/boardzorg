# SpiceBlow (--> Bidding or Nexu)

from copy import deepcopy

from dune.actions import args
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds import nexus, bidding


class Gift(Action):
    name = "gift"
    ck_faction = "emperor"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Gift Requires Different Arguments")

        other_faction, spice = parts
        spice = int(spice)
        return Gift(faction, other_faction, spice)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Faction(), args.Spice())

    def __init__(self, faction, other_faction, spice):
        self.faction = faction
        self.other_faction = other_faction
        self.spice = spice

    def _execute(self, game_state):
        if "emperor" not in game_state.alliances[self.other_faction]:
            raise IllegalAction("The emperor can only gift spice to allies.")

        if game_state.faction_state[self.faction].spice < self.spice:
            raise IllegalAction("Insufficient spice for this gift")

        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].spice -= self.spice
        new_game_state.faction_state[self.other_faction].bribe_spice += self.spice

        return new_game_state


class Bribe(Action):
    name = "bribe"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Bribe Requires Different Arguments")

        other_faction, spice = parts
        spice = int(spice)
        return Bribe(faction, other_faction, spice)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Faction(), args.Spice())

    def __init__(self, faction, other_faction, spice):
        self.faction = faction
        self.other_faction = other_faction
        self.spice = spice

    def _execute(self, game_state):
        if game_state.faction_state[self.faction].spice < self.spice:
            raise BadCommand("Insufficient spice for this bribe")

        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].spice -= self.spice
        new_game_state.faction_state[self.other_faction].bribe_spice += self.spice
        return new_game_state


class SpiceBlow(Action):
    name = "spice-blow"
    ck_round = "spice"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        card = new_game_state.spice_deck.pop(0)
        if card == "Shai-Hulud":
            previous_space = None
            for c in new_game_state.spice_discard:
                if not c != "Shai-Hulud":
                    previous_space = new_game_state.map_state[c]
                    break

            new_game_state.shai_hulud = previous_space
            new_game_state.round_state = nexus.NexusRound()
        else:
            space = new_game_state.map_state[card]
            if new_game_state.storm_position != space.spice_sector:
                space.spice = space.spice_amount
            new_game_state.round_state = bidding.BiddingRound()

        new_game_state.spice_discard.insert(0, card)

        return new_game_state
