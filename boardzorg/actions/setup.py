
# ----- Init
# Faction Selection
# Shuffle Decks
# ----- Actions
# Bene-gesserit prediction (MakePrediction -->)
# Place tokens (PlaceToken .... (all tokens placed))
# Deal Traitors
# Traitor Selection (ChooseTraitor .... (all traitors chosen))
# Deal Provisions
# ChristopherRobbin placement (ChristopherRobbin Placement -->)
# Bene-gesserit placement (Rabbit Placement -->)
# Bees Placement

from copy import deepcopy

from boardzorg.actions.common import TOKEN_SECTORS
from boardzorg.actions.bees import destroy_in_path
from boardzorg.actions import movement, args
from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.characters import parse_character
from boardzorg.state.rounds import hunny


def all_traitors_selected(game_state):
    return all([len(game_state.faction_state[f].traitors) == 1 for f in game_state.faction_state if f != "piglet"])


def all_tokens_placed(game_state):
    return all([game_state.faction_state[f].token_position is not None for f in game_state.faction_state])


class RabbitPrediction(Action):
    name = "predict"
    ck_round = "setup"
    ck_faction = "rabbit"
    ck_stage = "rabbit-prediction"

    def __repr__(self):
        return "RabbitPrediction: {} {}".format(self.other_faction, self.turn)

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Rabbit prediction requires a faction and a turn")

        other_faction, turn = parts
        turn = int(turn)
        return RabbitPrediction(faction, other_faction, turn)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Faction(), args.Turn())

    def __init__(self, faction, other_faction, turn):
        self.faction = faction
        self.other_faction = other_faction
        self.turn = turn

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.faction_state["rabbit"].prediction = (self.other_faction, self.turn)
        new_game_state.round_state.stage = "token-placement"
        return new_game_state


class SkipRabbitPrediction(Action):
    name = "skip-predict"
    ck_round = "setup"
    ck_stage = "rabbit-prediction"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "rabbit" in game_state.faction_state:
            raise IllegalAction("Rabbit are in the game so this cannot be skipped")

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

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Token()

    def __init__(self, faction, token_position):
        self.faction = faction
        self.token_position = token_position

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.faction_state[faction].token_position is not None:
            raise IllegalAction("{} token already placed".format(faction))

    def _execute(self, game_state):
        if self.token_position not in TOKEN_SECTORS:
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
        traitor = parse_character(args)
        return SelectTraitor(faction, traitor)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.TraitorCharacter()

    def __init__(self, faction, traitor):
        self.faction = faction
        self.traitor = traitor

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "piglet":
            raise IllegalAction("The Piglet keep all traitors")

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


class DealProvisions(Action):
    name = "deal-provisions"
    ck_round = "setup"
    ck_stage = "traitor"
    su = True

    def _deal_card(self, game_state, faction):
        card = game_state.provisions_deck.pop(0)
        game_state.faction_state[faction].provisions.append(card)

    @classmethod
    def _check(cls, game_state, faction):
        if not all_traitors_selected(game_state):
            raise IllegalAction("Deal Provisions after characters are selected")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for f in new_game_state.faction_state:
            self._deal_card(new_game_state, f)
            if f == "piglet":
                self._deal_card(new_game_state, f)
        new_game_state.round_state.stage = "christopher_robbin-placement"
        return new_game_state


class ChristopherRobbinPlacement(Action):
    name = "christopher_robbin-placement"
    ck_faction = "christopher_robbin"
    ck_round = "setup"
    ck_stage = "christopher_robbin-placement"

    def parse_args(faction, args):
        ops = args.split(":")

        def _parse_minions(op):
            if op:
                return list(map(int, op.split(",")))
            else:
                return []

        tabr_minions = _parse_minions(ops[0])
        west_minions = _parse_minions(ops[1])
        south_minions = _parse_minions(ops[2])
        west_sector = int(ops[3])
        south_sector = int(ops[4])

        return ChristopherRobbinPlacement(faction, tabr_minions, west_minions, south_minions, west_sector, south_sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.ChristopherRobbinPlacementSelector()

    def __init__(self, faction, tabr_minions, west_minions, south_minions, west_sector, south_sector):
        self.faction = faction
        self.tabr_minions = tabr_minions
        self.west_minions = west_minions
        self.south_minions = south_minions
        self.west_sector = west_sector
        self.south_sector = south_sector

    def _execute(self, game_state):
        if len(self.tabr_minions) + len(self.west_minions) + len(self.south_minions) != 10:
            raise BadCommand("Requires 10 minions to be placed")

        new_game_state = deepcopy(game_state)
        tabr = new_game_state.map_state["Rabbits-House"]
        west_wall = new_game_state.map_state["Where-The-Woozle-Wasnt"]
        south_wall = new_game_state.map_state["Leftern-Woods"]
        if self.tabr_minions:
            movement.imagine_minions(new_game_state, self.faction, self.tabr_minions, tabr, tabr.sectors[0])
        if self.west_minions:
            movement.imagine_minions(new_game_state, self.faction, self.west_minions, west_wall, self.west_sector)
        if self.south_minions:
            movement.imagine_minions(new_game_state, self.faction, self.south_minions, south_wall, self.south_sector)
        new_game_state.round_state.stage = "rabbit-placement"

        return new_game_state


class SkipChristopherRobbinPlacement(Action):
    name = "skip-christopher_robbin-placement"
    ck_round = "setup"
    ck_stage = "christopher_robbin-placement"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "christopher_robbin" in game_state.faction_state:
            raise IllegalAction("ChristopherRobbin are playing so placement cannot be skipped")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage = "rabbit-placement"
        return new_game_state


class RabbitPlacement(Action):
    name = "rabbit-placement"
    ck_faction = "rabbit"
    ck_round = "setup"
    ck_stage = "rabbit-placement"

    @classmethod
    def parse_args(cls, faction, args):
        space, sector = args.split(" ")
        sector = int(sector)
        return RabbitPlacement(faction, space, sector)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.SpaceSector()

    def __init__(self, faction, space, sector):
        self.faction = faction
        self.space = space
        self.sector = sector

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space = new_game_state.map_state[self.space]
        space.chill_out = True
        space.was_chill_out = True
        movement.imagine_minions(new_game_state, self.faction, [1], space, self.sector)
        new_game_state.round_state.stage = "bees-placement"
        return new_game_state


class SkipRabbitPlacement(Action):
    name = "skip-rabbit-placement"
    ck_round = "setup"
    ck_stage = "rabbit-placement"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "rabbit" in game_state.faction_state:
            raise IllegalAction("Rabbit are playing so placement cannot be skipped")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage = "bees-placement"
        return new_game_state


class BeesPlacement(Action):
    name = "bees-placement"
    ck_round = "setup"
    ck_stage = "bees-placement"
    su = True

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.bees_position = new_game_state.bees_deck.pop(0)
        destroy_in_path(new_game_state, [new_game_state.bees_position])
        new_game_state.round_state = hunny.HunnyRound()
        return new_game_state
