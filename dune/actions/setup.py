
# ----- Init
# Faction Selection
# Shuffle Decks
# ----- Actions
# Bene-gesserit prediction (MakePrediction -->)
# Place tokens (PlaceToken .... (all tokens placed))
# Deal Traitors
# Traitor Selection (ChooseTraitor .... (all traitors chosen))
# Deal Treachery
# Fremen placement (Fremen Placement -->)
# Bene-gesserit placement (Bene-Gesserit Placement -->)
# Storm Placement

from copy import deepcopy
from random import shuffle, randint

from dune.actions import movement, storm
from dune.actions.action import Action
from dune.constants import TOKEN_SECTORS
from dune.exceptions import IllegalAction, BadCommand
from dune.factions import FACTIONS
from dune.state.leader import LEADERS, parse_leader
from dune.state.state import SpiceState


def all_traitors_selected(game_state):
    return all([len(game_state.faction_state[f].traitors) == 1 for f in FACTIONS if f != "harkonnen"])


def all_tokens_placed(game_state):
    return all([game_state.faction_state[f].token_position is not None for f in FACTIONS])


class BeneGesseritPrediction(Action):
    name = "predict"
    ck_round = "setup"
    ck_faction = "bene-gesserit"

    def __repr__(self):
        return "BeneGesseritPrediction: {} {}".format(self.other_faction, self.turn)

    @classmethod
    def parse_args(cls, faction, args):
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

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.faction_state["bene-gesserit"].prediction != (None, 0):
            raise IllegalAction("Prediciton Already Made")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state["bene-gesserit"].prediction = (self.other_faction, self.turn)
        return new_game_state


class PlaceToken(Action):
    name = "place-token"
    ck_round = "setup"

    @classmethod
    def parse_args(cls, faction, args):
        return PlaceToken(faction, int(args))

    def __init__(self, faction, token_position):
        self.faction = faction
        self.token_position = token_position

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.faction_state["bene-gesserit"].prediction == (None, 0):
            raise IllegalAction("Token Placement happens after Bene-Gesserit Prediction")
        if game_state.faction_state[faction].token_position is not None:
            raise IllegalAction("{} token already placed".format(faction))

    def _execute(self, game_state):
        if self.token_position not in TOKEN_SECTORS:
            raise IllegalAction("Not a valid token position")

        for f in FACTIONS:
            if game_state.faction_state[f].token_position == self.token_position:
                raise IllegalAction("Token position already taken")

        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].token_position = self.token_position
        return new_game_state


class DealTraitors(Action):
    name = "deal-traitors"
    ck_round = "setup"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not all_tokens_placed(game_state):
            raise IllegalAction("Deal Traitors after tokens are placed")

        for f in game_state.faction_state:
            if game_state.faction_state[f].traitors:
                raise IllegalAction("Traitors already dealt")

    def _execute(self, game_state):
        all_leaders = [item for sublist in LEADERS.values() for item in sublist]
        shuffle(all_leaders)
        new_game_state = deepcopy(game_state)
        for f in new_game_state.faction_state:
            new_game_state.faction_state[f].traitors.append(all_leaders.pop())
            new_game_state.faction_state[f].traitors.append(all_leaders.pop())
            new_game_state.faction_state[f].traitors.append(all_leaders.pop())
            new_game_state.faction_state[f].traitors.append(all_leaders.pop())
        return new_game_state


class SelectTraitor(Action):
    name = "select-traitor"
    ck_round = "setup"

    def parse_args(faction, args):
        traitor = parse_leader(args)
        return SelectTraitor(faction, traitor)

    def __init__(self, faction, traitor):
        self.faction = faction
        self.traitor = traitor

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "harkonnen":
            raise IllegalAction("The Harkonnen keep all traitors")

        if not game_state.faction_state[faction].traitors:
            raise IllegalAction("Traitors have not been dealt")

        if len(game_state.faction_state[faction].traitors) == 1:
            raise IllegalAction("Traitors has already been selected")

    def _execute(self, game_state):
        if self.traitor not in game_state.faction_state[self.faction].traitors:
            raise IllegalAction("That traitor is not available for selection")

        new_game_state = deepcopy(game_state)
        old_traitors = new_game_state.faction_state[self.faction].traitors
        old_traitors.remove(self.traitor)
        new_game_state.faction_state[self.faction].rejected_traitors = old_traitors
        new_game_state.faction_state[self.faction].traitors = [self.traitor]
        return new_game_state


class DealTreachery(Action):
    name = "deal-treachery"
    ck_round = "setup"
    su = True

    def _deal_card(self, game_state, faction):
        card = game_state.treachery_deck.pop(0)
        game_state.faction_state[faction].treachery.append(card)

    @classmethod
    def _check(cls, game_state, faction):
        if not all_traitors_selected(game_state):
            raise IllegalAction("Deal Treachery after leaders are selected")
        for f in game_state.faction_state:
            if game_state.faction_state[f].treachery:
                raise IllegalAction("Treachery already dealt")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for f in new_game_state.faction_state:
            self._deal_card(new_game_state, f)
            if f == "harkonnen":
                self._deal_card(new_game_state, f)
        return new_game_state


class FremenPlacement(Action):
    name = "fremen-placement"
    ck_faction = "fremen"
    ck_round = "setup"

    def parse_args(faction, args):
        ops = args.split(" ")
        tabr_units = []
        west_units = []
        south_units = []
        west_sector = None
        south_sector = None
        for op in ops:
            parts = op.split(":")
            if parts[0] == "tabr":
                tabr_units = [int(i) for i in parts[1].split(",")]
            elif parts[0] == "west":
                west_units = [int(i) for i in parts[2].split(",")]
                west_sector = int(parts[1])
            elif parts[0] == "south":
                south_units = [int(i) for i in parts[2].split(",")]
                south_sector = int(parts[1])

        return FremenPlacement(faction, tabr_units, west_units, south_units, west_sector, south_sector)

    def __init__(self, faction, tabr_units, west_units, south_units, west_sector, south_sector):
        self.faction = faction
        self.tabr_units = tabr_units
        self.west_units = west_units
        self.south_units = south_units
        self.west_sector = west_sector
        self.south_sector = south_sector

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.faction_state["bene-gesserit"].treachery:
            raise IllegalAction("Fremen placement happens after Treachery is dealt")

        if len(game_state.faction_state["fremen"].reserve_units) != 20:
            raise IllegalAction("Fremen placement has already happened")

    def _execute(self, game_state):
        if len(self.tabr_units) + len(self.west_units) + len(self.south_units) != 10:
            raise IllegalAction("Requires 10 units to be placed")

        new_game_state = deepcopy(game_state)
        tabr = new_game_state.board_state.map_state["Sietch-Tabr"]
        west_wall = new_game_state.board_state.map_state["False-Wall-West"]
        south_wall = new_game_state.board_state.map_state["False-Wall-South"]
        movement.ship_units(new_game_state, self.faction, self.tabr_units, tabr, tabr.sectors[0])
        movement.ship_units(new_game_state, self.faction, self.west_units, west_wall, self.west_sector)
        movement.ship_units(new_game_state, self.faction, self.south_units, south_wall, self.south_sector)

        return new_game_state


class BeneGesseritPlacement(Action):
    name = "bene-gesserit-placement"
    ck_faction = "bene-gesserit"
    ck_round = "setup"

    @classmethod
    def parse_args(cls, faction, args):
        space, sector = args.split(" ")
        sector = int(sector)
        return BeneGesseritPlacement(faction, space, sector)

    def __init__(self, faction, space, sector):
        self.faction = faction
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.faction_state["fremen"].reserve_units) == 20:
            raise IllegalAction("Bene-Gesserit Placement happens after Fremen Placement")

        if len(game_state.faction_state["bene-gesserit"].reserve_units) != 20:
            raise IllegalAction("Bene-Gesserit Placement has already happened")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space = new_game_state.board_state.map_state[self.space]
        movement.ship_units(new_game_state, self.faction, [1], space, self.sector)
        return new_game_state


class StormPlacement(Action):
    name = "storm-placement"
    ck_round = "setup"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if len(game_state.faction_state["bene-gesserit"].reserve_units) != 19:
            raise IllegalAction("Bene-Gesserit Placement must happen before storm is placed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.board_state.storm_position = randint(0, 17)
        new_game_state.board_state.storm_advance = randint(0, 6)
        storm.destroy_in_path(new_game_state, [new_game_state.board_state.storm_position])
        new_game_state.round_state = SpiceState()
        return new_game_state
