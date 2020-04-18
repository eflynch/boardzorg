# SpiceBlow (--> Bidding or Nexu)

from copy import deepcopy

from dune.actions import args
from dune.actions.action import Action
from dune.actions.karama import discard_karama
from dune.exceptions import IllegalAction, BadCommand
from dune.state.rounds import nexus, bidding, spice
from dune.actions.common import get_faction_order, spend_spice
from dune.actions.movement import move_units


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


def _shai_hulud_eat_forces(game_state, faction):
    space = game_state.map_state[game_state.shai_hulud]
    if faction == "bene-gesserit":
        space.coexist = False
    del space.forces[faction]


def _progress_worm(game_state):
    factions = game_state.round_state.stage_state.factions
    faction_turn = game_state.round_state.stage_state.faction_turn
    turn_index = factions.index(faction_turn) if faction_turn else -1
    if turn_index == len(factions) - 1:
        # we're all done!
        game_state.round_state.stage = "fremen-worm-karama"
    else:
        game_state.round_state.stage_state.faction_turn = factions[turn_index + 1]
        game_state.round_state.stage_state.substage_state = spice.HandleWormForces()


def _shai_hulud(game_state, space_name):
    space = game_state.map_state[space_name]
    if 'sand' not in space.type:
        raise BadCommand("Sandworms can only appear in sandy areas.")

    game_state.shai_hulud = space_name
    game_state.round_state.needs_nexus = True

    space.spice = 0

    factions = list(space.forces.keys())

    # Immediately kill everyone who's not in a fremen alliance
    fremen_and_friends = set(["fremen"]) | game_state.alliances["fremen"]
    for faction in factions:
        if faction not in fremen_and_friends:
            _shai_hulud_eat_forces(game_state, faction)

    factions_left = [faction for faction in get_faction_order(game_state) if
                     faction in space.forces]

    if len(factions_left):
        game_state.round_state.stage_state = spice.ResolveWormStage(factions_left)
        _progress_worm(game_state)
    else:
        game_state.round_state.stage = "fremen-worm-karama"
    game_state.round_state.fremen_can_redirect_worm = True


def _draw_spice_card(game_state):
    card = game_state.spice_deck.pop(0)
    if card == "Shai-Hulud":
        if game_state.round_state.fremen_can_redirect_worm:
            game_state.round_state.stage = "fremen-redirect-worm"
        else:
            previous_space = None
            for c in game_state.spice_discard:
                if c != "Shai-Hulud":
                    previous_space = c
                    break

            _shai_hulud(game_state, previous_space)
    else:
        space = game_state.map_state[card]
        if game_state.storm_position != space.spice_sector:
            space.spice = space.spice_amount
        game_state.round_state.drawn_card = True
        game_state.round_state.stage = "fremen-worm-karama"

    game_state.spice_discard.insert(0, card)


class PassFremenWormKarama(Action):
    name = "pass-fremen-worm-karama"
    ck_round = "spice"
    ck_stage = "fremen-worm-karama"
    ck_faction = "fremen"

    @classmethod
    def _check(cls, game_state, faction):
        return game_state.turn > 1

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        if new_game_state.round_state.drawn_card:
            new_game_state.round_state = (nexus.NexusRound()
                                      if new_game_state.round_state.needs_nexus
                                      else bidding.BiddingRound())
        else:
            _draw_spice_card(new_game_state)
        return new_game_state


class FremenWormKarama(Action):
    name = "fremen-worm-karama"
    ck_round = "spice"
    ck_stage = "fremen-worm-karama"
    ck_faction = "fremen"
    ck_karama = True

    @classmethod
    def parse_args(cls, faction, args):
        return FremenWormKarama(faction, args)

    @classmethod
    def _check(cls, game_state, faction):
        return game_state.turn > 1

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Space()

    def __init__(self, faction, space):
        self.faction = faction
        self.space = space

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _shai_hulud(new_game_state, self.space)
        discard_karama(new_game_state, "fremen")
        return new_game_state


class KaramaWorm(Action):
    name = "karama-worm"
    ck_round = "spice"
    ck_stage = "worm"
    ck_karama = True

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "fremen":
            raise IllegalAction("You can't karama your own desert powers")

        if faction in game_state.round_state.stage_state.substage_state.karama_passes:
            raise IllegalAction("You already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _shai_hulud_eat_forces(new_game_state,
                               new_game_state.round_state.stage_state.faction_turn)
        _progress_worm(new_game_state)
        discard_karama(new_game_state, self.faction)
        return new_game_state


class KaramaPassWormRide(Action):
    name = "karama-pass-worm"
    ck_round = "spice"
    ck_stage = "worm"

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "fremen":
            raise IllegalAction("You can't karama your own desert powers")

        if faction in game_state.round_state.stage_state.substage_state.karama_passes:
            raise IllegalAction("You already passed karama")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.karama_passes.append(self.faction)
        return new_game_state


class WormRide(Action):
    name = "ride"
    ck_round = "spice"
    ck_stage = "worm"
    ck_faction = "fremen"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            units, space, sector = parts
        else:
            raise BadCommand("wrong number of args")

        if units == "":
            raise BadCommand("No units selected")
        units = [int(u) for u in units.split(",")]
        return WormRide(faction, units, space, int(sector))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Units(faction), args.SpaceSector())

    def __init__(self, faction, units, space, sector):
        self.faction = faction
        self.units = units
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.faction_turn:
            raise IllegalAction("It's not your turn to face the worm!")

        if len(game_state.round_state.stage_state.substage_state.karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Karama will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space = new_game_state.map_state[new_game_state.shai_hulud]
        new_space = new_game_state.map_state[self.space]

        for s in space.forces[self.faction]:
            move_units(new_game_state, self.faction, self.units, space, s, new_space, self.sector)

        _progress_worm(new_game_state)

        return new_game_state


class PassWormRide(Action):
    name = "pass-ride"
    ck_round = "spice"
    ck_stage = "worm"
    ck_faction = "fremen"

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.faction_turn:
            raise IllegalAction("It's not your turn to face the worm!")

        if len(game_state.round_state.stage_state.substage_state.karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Karama will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _progress_worm(new_game_state)
        return new_game_state


class ProtectFromWorm(Action):
    name = "protect"
    ck_round = "spice"
    ck_stage = "worm"
    ck_faction = "fremen"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.faction_turn == "fremen":
            raise IllegalAction("Fremen ride the worm rather than be protected by it")
        if len(game_state.round_state.stage_state.substage_state.karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Karama will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _progress_worm(new_game_state)
        return new_game_state


class PassProtectFromWorm(Action):
    name = "pass-protect"
    ck_round = "spice"
    ck_stage = "worm"
    ck_faction = "fremen"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.faction_turn == "fremen":
            raise IllegalAction("Fremen ride the worm rather than be protected by it")
        if len(game_state.round_state.stage_state.substage_state.karama_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Karama will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _shai_hulud_eat_forces(new_game_state,
                               new_game_state.round_state.stage_state.faction_turn)
        _progress_worm(new_game_state)
        return new_game_state


class FremenRedirectWorm(Action):
    name = "fremen-redirect-worm"
    ck_round = "spice"
    ck_stage = "fremen-redirect-worm"

    @classmethod
    def parse_args(cls, faction, args):
        return FremenRedirectWorm(faction, args)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Space()

    def __init__(self, faction, space):
        self.faction = faction
        self.space = space

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _shai_hulud(new_game_state, self.space)
        return new_game_state


class FirstTurnSpiceBlow(Action):
    name = "first-turn-spice-blow"
    ck_round = "spice"
    ck_stage = "fremen-worm-karama"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.turn != 1:
            raise IllegalAction("There's only one first time")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        while True:
            card = new_game_state.spice_deck.pop(0)
            new_game_state.spice_discard.insert(0, card)
            if card == "Shai-Hulud":
                continue

            space = game_state.map_state[card]
            if new_game_state.storm_position != space.spice_sector:
                space.spice = space.spice_amount
            new_game_state.round_state = bidding.BiddingRound()
            return new_game_state



