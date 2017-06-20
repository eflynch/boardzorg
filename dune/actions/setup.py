
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

from dune.actions import movement, storm
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand
from dune.state.leaders import parse_leader


def all_traitors_selected(game_state):
    return all([len(game_state.faction_state[f].traitors) == 1 for f in game_state.faction_state if f != "harkonnen"])


def all_tokens_placed(game_state):
    return all([game_state.faction_state[f].token_position is not None for f in game_state.faction_state])


class BeneGesseritPrediction(Action):
    name = "predict"
    ck_round = "setup"
    ck_faction = "bene-gesserit"
    ck_stage = "bene-gesserit-prediction"

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

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state["bene-gesserit"].prediction = (self.other_faction, self.turn)
        new_game_state.round_state.stage = "token-placement"
        return new_game_state


class SkipBeneGesseritPrediction(Action):
    name = "skip-predict"
    ck_round = "setup"
    ck_stage = "bene-gesserit-prediction"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "bene-gesserit" in game_state.faction_state:
            raise IllegalAction("Bene-Gesserit are in the game so this cannot be skipped")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage = "token-placement"
        return new_game_state


class PlaceToken(Action):
    name = "place-token"
    ck_round = "setup"
    ck_stage = "token-placement"

    @classmethod
    def parse_args(cls, faction, args):
        return PlaceToken(faction, int(args))

    def __init__(self, faction, token_position):
        self.faction = faction
        self.token_position = token_position

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.faction_state[faction].token_position is not None:
            raise IllegalAction("{} token already placed".format(faction))

    def _execute(self, game_state):
        if self.token_position not in storm.TOKEN_SECTORS:
            raise BadCommand("Not a valid token position")

        for f in game_state.faction_state:
            if game_state.faction_state[f].token_position == self.token_position:
                raise BadCommand("Token position already taken")

        new_game_state = deepcopy(game_state)
        new_game_state.faction_state[self.faction].token_position = self.token_position
        return new_game_state


class DealTraitors(Action):
    name = "deal-traitors"
    ck_round = "setup"
    ck_stage = "token-placement"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if not all_tokens_placed(game_state):
            raise IllegalAction("Deal Traitors after tokens are placed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for f in new_game_state.faction_state:
            new_game_state.faction_state[f].traitors.append(new_game_state.traitor_deck.pop(0))
            new_game_state.faction_state[f].traitors.append(new_game_state.traitor_deck.pop(0))
            new_game_state.faction_state[f].traitors.append(new_game_state.traitor_deck.pop(0))
            new_game_state.faction_state[f].traitors.append(new_game_state.traitor_deck.pop(0))
        new_game_state.round_state.stage = "traitor"
        return new_game_state


class SelectTraitor(Action):
    name = "select-traitor"
    ck_round = "setup"
    ck_stage = "traitor"

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

        if len(game_state.faction_state[faction].traitors) == 1:
            raise IllegalAction("Traitor has already been selected")

    def _execute(self, game_state):
        if self.traitor not in game_state.faction_state[self.faction].traitors:
            raise BadCommand(
                "{} traitor is not available for selection.\nValid Traitors are: {}".format(self.traitor,
                    ", ".join([t[0] for t in game_state.faction_state[self.faction].traitors])))

        new_game_state = deepcopy(game_state)
        old_traitors = new_game_state.faction_state[self.faction].traitors
        old_traitors.remove(self.traitor)
        new_game_state.faction_state[self.faction].rejected_traitors = old_traitors
        new_game_state.faction_state[self.faction].traitors = [self.traitor]
        return new_game_state


class DealTreachery(Action):
    name = "deal-treachery"
    ck_round = "setup"
    ck_stage = "traitor"
    su = True

    def _deal_card(self, game_state, faction):
        card = game_state.treachery_deck.pop(0)
        game_state.faction_state[faction].treachery.append(card)

    @classmethod
    def _check(cls, game_state, faction):
        if not all_traitors_selected(game_state):
            raise IllegalAction("Deal Treachery after leaders are selected")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for f in new_game_state.faction_state:
            self._deal_card(new_game_state, f)
            if f == "harkonnen":
                self._deal_card(new_game_state, f)
        new_game_state.round_state.stage = "fremen-placement"
        return new_game_state


class FremenPlacement(Action):
    name = "fremen-placement"
    ck_faction = "fremen"
    ck_round = "setup"
    ck_stage = "fremen-placement"

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

    def _execute(self, game_state):
        if len(self.tabr_units) + len(self.west_units) + len(self.south_units) != 10:
            raise BadCommand("Requires 10 units to be placed")

        new_game_state = deepcopy(game_state)
        tabr = new_game_state.map_state["Sietch-Tabr"]
        west_wall = new_game_state.map_state["False-Wall-West"]
        south_wall = new_game_state.map_state["False-Wall-South"]
        if self.tabr_units:
            movement.ship_units(new_game_state, self.faction, self.tabr_units, tabr, tabr.sectors[0])
        if self.west_units:
            movement.ship_units(new_game_state, self.faction, self.west_units, west_wall, self.west_sector)
        if self.south_units:
            movement.ship_units(new_game_state, self.faction, self.south_units, south_wall, self.south_sector)
        new_game_state.round_state.stage = "bene-gesserit-placement"

        return new_game_state


class SkipFremenPlacement(Action):
    name = "skip-fremen-placement"
    ck_round = "setup"
    ck_stage = "fremen-placement"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "fremen" in game_state.faction_state:
            raise IllegalAction("Fremen are playing so placement cannot be skipped")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage = "bene-gesserit-placement"
        return new_game_state


class BeneGesseritPlacement(Action):
    name = "bene-gesserit-placement"
    ck_faction = "bene-gesserit"
    ck_round = "setup"
    ck_stage = "bene-gesserit-placement"

    @classmethod
    def parse_args(cls, faction, args):
        space, sector = args.split(" ")
        sector = int(sector)
        return BeneGesseritPlacement(faction, space, sector)

    def __init__(self, faction, space, sector):
        self.faction = faction
        self.space = space
        self.sector = sector

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space = new_game_state.map_state[self.space]
        space.coexist = True
        movement.ship_units(new_game_state, self.faction, [1], space, self.sector)
        new_game_state.round_state.stage = "storm-placement"
        return new_game_state


class SkipBeneGesseritPlacement(Action):
    name = "skip-bene-gesserit-placement"
    ck_round = "setup"
    ck_stage = "bene-gesserit-placement"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "bene-gesserit" in game_state.faction_state:
            raise IllegalAction("Bene-Gesserit are playing so placement cannot be skipped")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage = "storm-placement"
        return new_game_state


class StormPlacement(Action):
    name = "storm-placement"
    ck_round = "setup"
    ck_stage = "storm-placement"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.storm_position = new_game_state.storm_deck.pop(0)
        storm.destroy_in_path(new_game_state, [new_game_state.storm_position])
        new_game_state.round = "spice"
        return new_game_state
