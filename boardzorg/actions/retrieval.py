from copy import deepcopy

from boardzorg.actions import bees, args
from boardzorg.actions.common import get_faction_order, spend_hunny
from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction, BadCommand
from boardzorg.state.rounds.movement import MovementRound
from boardzorg.state.characters import parse_character
from boardzorg.actions.author import discard_author


def get_revivable_characters(game_state, faction):
    fs = game_state.faction_state[faction]
    non_captured_characters = [character[0] for character in fs.characters[:] + fs.lost_characters[:]]

    character_death_count = game_state.faction_state[faction].character_death_count

    def _ldc(character_name):
        if character_name in character_death_count:
            return character_death_count[character_name]
        else:
            return 0

    min_count = min([_ldc(character_name) for character_name in non_captured_characters])

    all_revivable_characters = []

    if faction == "owl":
        winnie_the_pooh_losts = fs.winnie_the_pooh_losts
        if winnie_the_pooh_losts is not None and winnie_the_pooh_losts <= min_count:
            all_revivable_characters.append(("Winnie-The-Pooh", 2))

    for character in fs.lost_characters:
        if _ldc(character[0]) <= min_count:
            all_revivable_characters.append(character)

    return all_revivable_characters


class ProgressRetrieval(Action):
    name = "progress-retrieval"
    ck_round = "retrieval"
    su = True

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.round_state.faction_turn is not None:
            if get_revivable_characters(game_state, game_state.round_state.faction_turn):
                raise IllegalAction("They might want to revive that character")

            if game_state.faction_state[game_state.round_state.faction_turn].lost_minions:
                raise IllegalAction("They might want to revive those minions")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        for faction in get_faction_order(game_state):
            if faction in game_state.round_state.factions_done:
                continue
            if game_state.faction_state[faction].lost_minions:
                new_game_state.round_state.faction_turn = faction
                return new_game_state
            if get_revivable_characters(game_state, faction):
                new_game_state.round_state.faction_turn = faction
                return new_game_state

        new_game_state.round_state = MovementRound()
        return new_game_state


def parse_retrieval_minions(args):
    if not args:
        return []

    minions = []
    for i in args.split(","):
        if i in ["1", "2"]:
            minions.append(int(i))
        else:
            raise BadCommand("What sort of minion is _that_?")
    return minions


def parse_retrieval_character(args):
    if (args == "") or (args == "-"):
        return None
    if args == "Winnie-The-Pooh":
        return ("Winnie-The-Pooh", 2)
    else:
        return parse_character(args)


def _get_character_cost(character):
    return character[1] if character else 0


def _get_minion_cost(faction, minions, christopher_robbin_blessing=False):
    if christopher_robbin_blessing:
        return 0

    cost = len(minions) * 2
    if faction in ["eeyore", "rabbit", "kanga"]:
        cost = max(0, cost - 2)
    if faction in ["owl", "piglet"]:
        cost = max(0, cost - 4)
    if faction == "christopher_robbin":
        cost = 0
    return cost


def revive_minions(minions, faction, game_state):
    for u in minions:
        if u not in game_state.faction_state[faction].lost_minions:
            raise BadCommand("Those minions are not in the losts")
        game_state.faction_state[faction].lost_minions.remove(u)
        game_state.faction_state[faction].reserve_minions.append(u)


def revive_character(character, faction, game_state):
    if character is not None:
        if character[0] == "Winnie-The-Pooh":
            if game_state.faction_state[faction].winnie_the_pooh_losts is None:
                raise BadCommand("There's no winnie the pooh to revive!")
            game_state.faction_state[faction].winnie_the_pooh_losts = None
        else:
            if character not in game_state.faction_state[faction].lost_characters:
                raise BadCommand("You can't revive that character, because they are not in the losts!")
            game_state.faction_state[faction].lost_characters.remove(character)
            game_state.faction_state[faction].characters.append(character)


def _execute_retrieval(minions, character, faction, game_state, cost):
    new_game_state = deepcopy(game_state)
    spend_hunny(new_game_state, faction, cost)
    revive_minions(minions, faction, new_game_state)
    revive_character(character, faction, new_game_state)

    return new_game_state


class AuthorFreeMinionRetrieval(Action):
    name = "author-free-minion-retrieval"
    ck_author = True
    ck_faction_author = "eeyore"

    def __init__(self, faction, minions):
        self.faction = faction
        self.minions = minions

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.faction_state[faction].lost_minions:
            raise IllegalAction("You don't have any minions to revive")

    @classmethod
    def parse_args(cls, faction, args):
        minions = parse_retrieval_minions(args)
        if not minions:
            raise IllegalAction("Can't revive no minions")
        return AuthorFreeMinionRetrieval(faction, minions)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.RetrievalMinions(game_state.faction_state[faction].lost_minions,
                                 single_2=False)

    def _execute(self, game_state):
        if len(self.minions) > 3:
            raise BadCommand("You can only revive up to three minions")
        new_game_state = deepcopy(game_state)
        revive_minions(self.minions, self.faction, new_game_state)
        discard_author(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_author = True
        return new_game_state


class AuthorFreeCharacterRetrieval(Action):
    name = "author-free-character-retrieval"
    ck_author = True
    ck_faction_author = "eeyore"

    def __init__(self, faction, character):
        self.faction = faction
        self.character = character

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.faction_state[faction].lost_characters:
            raise IllegalAction("You don't have any characters to revive")

    @classmethod
    def parse_args(cls, faction, args):
        character = parse_retrieval_character(args)
        if character is None:
            raise BadCommand("Can't revive not a character for free!")
        return AuthorFreeCharacterRetrieval(faction, character)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.RetrievalCharacter(game_state.faction_state[faction].lost_characters,
                                  required=True)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        revive_character(self.character, self.faction, new_game_state)
        discard_author(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_author = True
        return new_game_state


class ChristopherRobbinBlessing(Action):
    name = "allow-free-ally-retrieval"
    ck_round = "retrieval"
    ck_faction = "christopher_robbin"

    @classmethod
    def parse_args(cls, faction, args):
        allies = args.split(" ")
        return ChristopherRobbinBlessing(faction, allies)

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.alliances[faction]:
            raise IllegalAction("You cannot give allies free retrieval if you have no allies")

    def __init__(self, faction, allies):
        self.faction = faction
        self.allies = allies

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        factions = game_state.alliances[faction]
        return args.MultiFaction(factions=factions)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.christopher_robbin_blessings = []
        for ally in self.allies:
            if ally not in new_game_state.alliances[self.faction]:
                raise BadCommand("You cannot give free retrieval to non-allies")
            new_game_state.round_state.christopher_robbin_blessings.append(ally)
        return new_game_state


class EeyoreAllyRetrieval(Action):
    name = "revive-ally-minions"
    ck_round = "retrieval"
    ck_faction = "eeyore"

    @classmethod
    def parse_args(cls, faction, args):
        parts = args.split(" ") if args != "" else []
        if len(parts) % 2 != 0:
            raise BadCommand("Need to specify minions and faction per ally")

        retrievals = {}
        for i in range(0, len(parts), 2):
            ally = parts[i]
            minions = parts[i+1]
            minions = parse_retrieval_minions(minions)
            retrievals[ally] = minions

        return EeyoreAllyRetrieval(faction, retrievals)

    @classmethod
    def _check(cls, game_state, faction):
        if not game_state.alliances[faction]:
            raise IllegalAction("You cannot give allies free retrievals if you have no allies")
        if game_state.round_state.eeyore_ally_retrieval_done:
            raise IllegalAction("You already did your special retrieval")

    def __init__(self, faction, retrievals):
        self.faction = faction
        self.retrievals = retrievals

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        retrievals = []
        for f in game_state.alliances[faction]:
            retrievals.append(args.RetrievalMinions(
                game_state.faction_state[faction].lost_minions,
                max_minions=3,
                single_2=False,
                title=f))
        return args.Struct(*retrievals)

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.round_state.eeyore_ally_retrieval_done = True
        for ally in self.retrievals:
            if ally not in new_game_state.alliances[self.faction]:
                raise BadCommand("You cannot give free retrieval to non-allies")
            minions = self.retrievals[ally]
            if len(minions) > 3:
                raise BadComand("You can only revive 3 minions for your allies")

            cost = 2 * len(minions)
            spend_hunny(new_game_state, self.faction, cost)
            revive_minions(minions, ally, new_game_state)
        new_game_state.round_state.eeyore_ally_retrieval_done = True
        return new_game_state


class Revive(Action):
    name = "revive"
    ck_round = "retrieval"

    @classmethod
    def parse_args(cls, faction, args):
        if not args:
            return Revive(faction, [], None)
        minions, character = args.split(" ")
        return Revive(faction, parse_retrieval_minions(minions), parse_retrieval_character(character))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(
            args.RetrievalMinions(game_state.faction_state[faction].lost_minions),
            args.RetrievalCharacter(get_revivable_characters(game_state, faction))
        )

    def __init__(self, faction, minions, character):
        self.faction = faction
        self.minions = minions
        self.character = character

    @classmethod
    def _check(cls, game_state, faction):
        if (not game_state.faction_state[faction].lost_minions) and \
           get_revivable_characters(game_state, faction):
            raise IllegalAction("You don't have anything to revive")
        Action.check_turn(game_state, faction)

    def _execute(self, game_state):
        if self.character and self.character not in get_revivable_characters(game_state, self.faction):
            raise BadCommand("That character is not revivable")
        if len(self.minions) > 3:
            raise BadCommand("You can only revive up to three minions")
        if self.minions.count("2") > 1:
            raise BadCommand("Only 1 Sardukar or Fedykin can be be revived per turn")

        has_christopher_robbin_blessing = self.faction in game_state.round_state.christopher_robbin_blessings
        cost = _get_minion_cost(self.faction, self.minions, has_christopher_robbin_blessing) + _get_character_cost(self.character)
        new_game_state = _execute_retrieval(self.minions, self.character, self.faction, game_state, cost)
        faction_order = get_faction_order(game_state)
        index = faction_order.index(self.faction) + 1
        if index < len(faction_order):
            new_game_state.round_state.factions_done.append(self.faction)
            new_game_state.round_state.faction_turn = faction_order[index]
        else:
            new_game_state.round_state = MovementRound()
        return new_game_state
