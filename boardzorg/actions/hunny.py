# HunnyBlow (--> Bidding or Picnick)

from copy import deepcopy

from boardzorg.actions import args
from boardzorg.actions.action import Action
from boardzorg.actions.author import discard_author
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.rounds import picnick, bidding, hunny
from boardzorg.actions.common import get_faction_order, spend_hunny
from boardzorg.actions.movement import move_minions
from boardzorg.actions.battle import ops


class Chat(Action):
    name = "chat"
    non_blocking = True
    _execute = None

    @classmethod
    def parse_args(cls, faction, args):
        return Chat(faction, args)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.String()

    def __init__(self, faction, message):
        self.faction = faction
        self.message = message


class Gift(Action):
    name = "gift"
    ck_faction = "eeyore"
    ck_pause_context = ["steal-provisions", "query-flip-frends_and_raletions", "query-flip-fighters"]
    non_blocking = True

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Gift Requires Different Arguments")

        other_faction, hunny = parts
        hunny = int(hunny)
        return Gift(faction, other_faction, hunny)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Faction(), args.Hunny())

    def __init__(self, faction, other_faction, hunny):
        self.faction = faction
        self.other_faction = other_faction
        self.hunny = hunny

    def _execute(self, game_state):
        if "eeyore" not in game_state.alliances[self.other_faction]:
            raise IllegalAction("The eeyore can only gift hunny to allies.")

        new_game_state = deepcopy(game_state)
        spend_hunny(new_game_state, self.faction, self.hunny)
        new_game_state.faction_state[self.other_faction].hunny += self.hunny

        return new_game_state


class Bribe(Action):
    name = "bribe"
    ck_pause_context = ["steal-provisions", "flip-to-frends_and_raletions", "flip-to-fighters"]
    non_blocking = True

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) != 2:
            raise BadCommand("Bribe Requires Different Arguments")

        other_faction, hunny = parts
        hunny = int(hunny)
        return Bribe(faction, other_faction, hunny)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Faction(), args.Hunny())

    def __init__(self, faction, other_faction, hunny):
        self.faction = faction
        self.other_faction = other_faction
        self.hunny = hunny

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)

        # Try to spend from bribe_hunny first
        to_spend = self.hunny
        if new_game_state.faction_state[self.faction].bribe_hunny:
            from_bribe = min(new_game_state.faction_state[self.faction].bribe_hunny, to_spend)
            new_game_state.faction_state[self.faction].bribe_hunny -= from_bribe
            to_spend -= from_bribe

        spend_hunny(new_game_state, self.faction, to_spend)

        new_game_state.faction_state[self.other_faction].bribe_hunny += self.hunny
        return new_game_state


def _heffalump_eat_forces(game_state, faction):
    space = game_state.map_state[game_state.heffalump]
    sectors = list(space.forces[faction].keys())
    for sec in sectors:
        for u in space.forces[faction][sec][:]:
            ops.lost_minion(game_state, faction, space, sec, u)


def _progress_heffalump(game_state):
    factions = game_state.round_state.stage_state.factions
    faction_turn = game_state.round_state.stage_state.faction_turn
    turn_index = factions.index(faction_turn) if faction_turn else -1
    if turn_index == len(factions) - 1:
        # we're all done!
        game_state.round_state.stage = "christopher_robbin-heffalump-author"
    else:
        game_state.round_state.stage_state.faction_turn = factions[turn_index + 1]
        game_state.round_state.stage_state.substage_state = hunny.HandleHeffalumpForces()


def _heffalump(game_state, space_name):
    space = game_state.map_state[space_name]
    if 'meadow' not in space.type:
        raise BadCommand("Meadowheffalumps can only appear in meadowy areas.")

    game_state.heffalump = space_name
    game_state.round_state.needs_picnick = True

    space.hunny = 0

    factions = list(space.forces.keys())

    # Immediately kill everyone who's not in a christopher_robbin alliance
    if "christopher_robbin" in game_state.faction_state:
        christopher_robbin_and_friends = set(["christopher_robbin"]) | game_state.alliances["christopher_robbin"]
    else:
        christopher_robbin_and_friends = []

    for faction in factions:
        if faction not in christopher_robbin_and_friends:
            _heffalump_eat_forces(game_state, faction)

    factions_left = [faction for faction in get_faction_order(game_state) if
                     faction in space.forces]

    if len(factions_left):
        game_state.round_state.stage_state = hunny.ResolveHeffalumpStage(factions_left)
        _progress_heffalump(game_state)
    else:
        game_state.round_state.stage = "christopher_robbin-heffalump-author"
    game_state.round_state.christopher_robbin_can_redirect_heffalump = True


def _draw_hunny_card(game_state):
    card = game_state.hunny_deck.pop(0)
    if card == "Heffalump":
        if game_state.round_state.christopher_robbin_can_redirect_heffalump and "christopher_robbin" in game_state.faction_state:
            game_state.round_state.stage = "christopher_robbin-redirect-heffalump"
        else:
            previous_space = None
            for c in game_state.hunny_discard:
                if c != "Heffalump":
                    previous_space = c
                    break

            _heffalump(game_state, previous_space)
    else:
        space = game_state.map_state[card]
        if game_state.bees_position != space.hunny_sector:
            space.hunny = space.hunny_amount
        game_state.round_state.drawn_card = True
        game_state.round_state.stage = "christopher_robbin-heffalump-author"

    game_state.hunny_discard.insert(0, card)


class SkipChristopherRobbinHeffalumpAuthor(Action):
    name = "skip-christopher_robbin-heffalump-author"
    ck_round = "hunny"
    ck_stage = "christopher_robbin-heffalump-author"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if "christopher_robbin" in game_state.faction_state and not game_state.faction_state["christopher_robbin"].used_faction_author:
            raise IllegalAction("ChristopherRobbin need the opportminiony to author a heffalump")
        if game_state.turn <= 1:
            raise IllegalAction("Cannot author heffalump on round 1")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        if new_game_state.round_state.drawn_card:
            new_game_state.round_state = (picnick.PicnickRound()
                                      if new_game_state.round_state.needs_picnick
                                      else bidding.BiddingRound())
        else:
            _draw_hunny_card(new_game_state)
        return new_game_state


class PassChristopherRobbinHeffalumpAuthor(Action):
    name = "pass-christopher_robbin-heffalump-author"
    ck_round = "hunny"
    ck_stage = "christopher_robbin-heffalump-author"
    ck_faction_author = "christopher_robbin"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.turn <= 1:
            raise IllegalAction("Cannot author heffalump on round 1")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        if new_game_state.round_state.drawn_card:
            new_game_state.round_state = (picnick.PicnickRound()
                                      if new_game_state.round_state.needs_picnick
                                      else bidding.BiddingRound())
        else:
            _draw_hunny_card(new_game_state)
        return new_game_state


class ChristopherRobbinHeffalumpAuthor(Action):
    name = "christopher_robbin-heffalump-author"
    ck_round = "hunny"
    ck_stage = "christopher_robbin-heffalump-author"
    ck_faction_author = "christopher_robbin"
    ck_author = True

    @classmethod
    def parse_args(cls, faction, args):
        return ChristopherRobbinHeffalumpAuthor(faction, args)

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.turn <= 1:
            raise IllegalAction("Cannot author heffalump on round 1")

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Space()

    def __init__(self, faction, space):
        self.faction = faction
        self.space = space

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _heffalump(new_game_state, self.space)
        discard_author(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_author = True
        return new_game_state


class AuthorHeffalump(Action):
    name = "author-heffalump"
    ck_round = "hunny"
    ck_stage = "heffalump"
    ck_author = True

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "christopher_robbin":
            raise IllegalAction("You can't author your own desert powers")

        if faction in game_state.round_state.stage_state.substage_state.author_passes:
            raise IllegalAction("You already passed")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _heffalump_eat_forces(new_game_state,
                               new_game_state.round_state.stage_state.faction_turn)
        _progress_heffalump(new_game_state)
        discard_author(new_game_state, self.faction)
        return new_game_state


class AuthorPassHeffalumpRide(Action):
    name = "author-pass-heffalump"
    ck_round = "hunny"
    ck_stage = "heffalump"

    def __init__(self, faction):
        self.faction = faction

    @classmethod
    def _check(cls, game_state, faction):
        if faction == "christopher_robbin":
            raise IllegalAction("You can't author your own desert powers")

        if faction in game_state.round_state.stage_state.substage_state.author_passes:
            raise IllegalAction("You already passed author")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.stage_state.substage_state.author_passes.append(self.faction)
        return new_game_state


class HeffalumpRide(Action):
    name = "ride"
    ck_round = "hunny"
    ck_stage = "heffalump"
    ck_faction = "christopher_robbin"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ")
        if len(parts) == 3:
            minions, space, sector = parts
        else:
            raise BadCommand("wrong number of args")

        if minions == "":
            raise BadCommand("No minions selected")
        minions = [int(u) for u in minions.split(",")]
        return HeffalumpRide(faction, minions, space, int(sector))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Minions(faction), args.SpaceSector())

    def __init__(self, faction, minions, space, sector):
        self.faction = faction
        self.minions = minions
        self.space = space
        self.sector = sector

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.faction_turn:
            raise IllegalAction("It's not your turn to face the heffalump!")

        if len(game_state.round_state.stage_state.substage_state.author_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Author will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        space = new_game_state.map_state[new_game_state.heffalump]
        new_space = new_game_state.map_state[self.space]

        for s in space.forces[self.faction]:
            move_minions(new_game_state, self.faction, self.minions, space, s, new_space, self.sector)

        _progress_heffalump(new_game_state)

        return new_game_state


class PassHeffalumpRide(Action):
    name = "pass-ride"
    ck_round = "hunny"
    ck_stage = "heffalump"
    ck_faction = "christopher_robbin"

    @classmethod
    def _check(cls, game_state, faction):
        if faction != game_state.round_state.stage_state.faction_turn:
            raise IllegalAction("It's not your turn to face the heffalump!")

        if len(game_state.round_state.stage_state.substage_state.author_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Author will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _progress_heffalump(new_game_state)
        return new_game_state


class ProtectFromHeffalump(Action):
    name = "protect"
    ck_round = "hunny"
    ck_stage = "heffalump"
    ck_faction = "christopher_robbin"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.faction_turn == "christopher_robbin":
            raise IllegalAction("ChristopherRobbin ride the heffalump rather than be protected by it")
        if len(game_state.round_state.stage_state.substage_state.author_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Author will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _progress_heffalump(new_game_state)
        return new_game_state


class PassProtectFromHeffalump(Action):
    name = "pass-protect"
    ck_round = "hunny"
    ck_stage = "heffalump"
    ck_faction = "christopher_robbin"

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.stage_state.faction_turn == "christopher_robbin":
            raise IllegalAction("ChristopherRobbin ride the heffalump rather than be protected by it")
        if len(game_state.round_state.stage_state.substage_state.author_passes) != len(game_state.faction_state) - 1:
            raise IllegalAction("Must wait to see if a Author will be used")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _heffalump_eat_forces(new_game_state,
                               new_game_state.round_state.stage_state.faction_turn)
        _progress_heffalump(new_game_state)
        return new_game_state


class ChristopherRobbinRedirectHeffalump(Action):
    name = "christopher_robbin-redirect-heffalump"
    ck_round = "hunny"
    ck_stage = "christopher_robbin-redirect-heffalump"
    ck_faction = "christopher_robbin"

    @classmethod
    def parse_args(cls, faction, args):
        return ChristopherRobbinRedirectHeffalump(faction, args)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Space()

    def __init__(self, faction, space):
        self.faction = faction
        self.space = space

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        _heffalump(new_game_state, self.space)
        return new_game_state


class FirstTurnHunnyBlow(Action):
    name = "first-turn-hunny-blow"
    ck_round = "hunny"
    ck_stage = "christopher_robbin-heffalump-author"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.turn != 1:
            raise IllegalAction("There's only one first time")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        while True:
            card = new_game_state.hunny_deck.pop(0)
            new_game_state.hunny_discard.insert(0, card)
            if card == "Heffalump":
                continue

            space = new_game_state.map_state[card]
            if new_game_state.bees_position != space.hunny_sector:
                space.hunny = space.hunny_amount
            new_game_state.round_state = bidding.BiddingRound()
            return new_game_state
