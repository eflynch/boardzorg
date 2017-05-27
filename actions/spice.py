from copy import deepcopy

from exceptions import IllegalAction, BadCommand

from actions.action import Action

from state import NexusState


class Gift(Action):
    def parse_args(faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Bribe Requires Different Arguments")

        other_faction, spice = parts
        spice = int(spice)
        return Bribe(faction, other_faction, spice)

    def __init__(self, faction, other_faction, spice):
        self.faction = faction
        self.other_faction = other_faction
        self.spice = spice

    def execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if self.faction != "emperor":
            raise IllegalAction("Only the emperor can gift spice")

        if "emperor" not in new_game_state.alliances[self.other_faction]:
            raise IllegalAction("The emperor can only gift spice to allies.")

        if new_game_state.faction_state[self.faction].spice < self.spice:
            raise IllegalAction("Insufficient spice for this gift")

        new_game_state.faction_state[self.faction].spice -= self.spice
        new_game_state.faction_state[self.other_faction].bribe_spice += self.spice

        return new_game_state


class Bribe(Action):
    def parse_args(faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Bribe Requires Different Arguments")

        other_faction, spice = parts
        spice = int(spice)
        return Bribe(faction, other_faction, spice)

    def __init__(self, faction, other_faction, spice):
        self.faction = faction
        self.other_faction = other_faction
        self.spice = spice

    def execute(self, game_state):
        new_game_state = deepcopy(game_state)

        if new_game_state.faction_state[self.faction].spice < self.spice:
            raise IllegalAction("Insufficient spice for this bribe")

        new_game_state.faction_state[self.faction].spice -= self.spice
        new_game_state.faction_state[self.other_faction].bribe_spice += self.spice

        return new_game_state


class SpiceBlow(Action):
    def execute(self, game_state):
        new_game_state = deepcopy(game_state)

        self.check_round("spice")

        card = new_game_state.board_state.spice_deck.pop(0)

        if card.shai_hulud:
            previous_space = None
            for c in new_game_state.board_state.spice_discard:
                if not c.shai_hulud:
                    previous_space = c.space
                    break

            new_game_state.board_state.shai_hulud = previous_space
            new_game_state.round_state = NexusState()

        new_game_state.board_state.spice_discard.insert(0, card)

        return new_game_state
