# SpiceBlow (--> Bidding or Nexu)

from copy import deepcopy

from dune.actions import args
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds import nexus, bidding


def spend_spice(game_state, faction, amount, context=None):
    spice_to_spend = game_state.faction_state[faction].spice
    if game_state.spice_context[faction] is not None:
        if game_state.spice_reserve[faction] is not None:
            if context == game_state.spice_context[faction]:
                game_state.spice_reserve[faction] = None
                game_state.spice_context[faction] = None
            else:
                spice_to_spend = game_state.faction_state[faction].spice - game_state.spice_reserve[faction]
    if amount > spice_to_spend:
        raise IllegalAction("Insufficient spice for this action")
    game_state.faction_state[faction].spice -= amount


class Gift(Action):
    name = "gift"
    ck_faction = "emperor"
    ck_pause_context = ["steal-treachery"]

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

        new_game_state = deepcopy(game_state)
        spend_spice(new_game_state, self.faction, self.spice)
        new_game_state.faction_state[self.other_faction].bribe_spice += self.spice

        return new_game_state


class Bribe(Action):
    name = "bribe"
    ck_pause_context = ["steal-treachery"]

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
        new_game_state = deepcopy(game_state)

        # Try to spend from bribe_spice first
        to_spend = self.spice
        if new_game_state.faction_state[self.faction].bribe_spice:
            from_bribe = min(new_game_state.faction_state[self.faction].bribe_spice, to_spend)
            new_game_state.faction_state[self.faction].bribe_spice -= from_bribe
            to_spend -= from_bribe

        spend_spice(new_game_state, self.faction, to_spend)

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
                if c != "Shai-Hulud":
                    previous_space = c
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
