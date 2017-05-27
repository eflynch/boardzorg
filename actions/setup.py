
# ----- Init
# Faction Selection
# Shuffle Decks
# ----- Actions
# Bene-gesserit prediction (MakePrediction -->)
# Place tokens (PlaceToken .... (all tokens placed))
# Traitor Selection (ChooseTraitor .... (all traitors chosen))
# Treachery Card Dealing (Deal Treachery Cards -->)
# Fremen placement (Fremen Placement -->)
# Bene-gesserit placement (Bene-Gesserit Placement -->)
#

from copy import deepcopy

from exceptions import IllegalAction, BadCommand
from factions import FACTIONS

from actions.action import Action


class BeneGesseritPrediction(Action):
    def parse_args(faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Bribe Requires Different Arguments")

        other_faction, turn = parts
        turn = int(turn)
        return BeneGesseritPrediction(faction, other_faction, turn)

    def __init__(self, faction, other_faction, turn):
        self.faction = faction
        self.other_faction = other_faction
        self.turn = turn

    def execute(self, game_state):
        self.check_faction("bene-gesserit")
        self.check_round("setup")

        if game_state.faction_state["bene-gesserit"].prediction != (None, 0):
            raise IllegalAction("Prediciton Already Made")

        new_game_state = deepcopy(game_state)

        new_game_state.faction_state["bene-gesserit"].prediction = (self.other_faction, self.turn)

        return new_game_state


class PlaceToken(Action):
    def parse_args(faction, args):
        return PlaceToken(faction, int(args))

    def __init__(self, faction, token_position):
        self.faction = faction
        self.token_position = token_position

    def execute(self, game_state):
        self.check_round("setup")
        if game_state.faction_state["bene-gesserit"].prediction == (None, 0):
            raise IllegalAction("Token Placement happens after Bene-Gesserit Prediction")
        if game_state.faction_state[self.faction].token_position is not None:
            raise IllegalAction("{} token already placed".format(self.faction))
        if self.token_position not in [1, 4, 7, 10, 13, 16]:
            raise IllegalAction("Not a valid token position")
        for f in FACTIONS:
            if game_state.faction_state[f].token_position == self.token_position:
                raise IllegalAction("Token position already taken")

        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].token_position = self.token_position
