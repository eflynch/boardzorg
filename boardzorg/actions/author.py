from copy import deepcopy

from boardzorg.state.provisions_cards import WORTHLESS
from boardzorg.actions import args
from boardzorg.actions.action import Action
from boardzorg.exceptions import IllegalAction, BadCommand


# For now, always use a worthless card before a author card
def discard_author(game_state, faction):
    t_deck = game_state.faction_state[faction].provisions
    k_card = "Author"
    if faction == "rabbit":
        worthless = [card for card in t_deck if card in WORTHLESS]
        if worthless:
            k_card = worthless[0]

    t_deck.remove(k_card)
    game_state.provisions_discard.insert(0, k_card)


class AuthorStealProvisions(Action):
    name = "author-steal-provisions"
    ck_author = True
    ck_faction_author = "piglet"
    non_blocking = True

    def __init__(self, faction, target_faction, number):
        self.faction = faction
        self.target_faction = target_faction
        self.number = number

    @classmethod
    def parse_args(cls, faction, args):
        target_faction, number = args.split(" ")
        return AuthorStealProvisions(faction, target_faction, int(number))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Faction(), args.Integer(min=0, max=4, type="Cards"))

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.pause_context = "steal-provisions"
        provisions = new_game_state.faction_state[self.target_faction].provisions[:]

        real_number = min(self.number, len(provisions))
        provisions_to_steal = []
        for i in range(real_number):
            choice = new_game_state.random_choice_deck.pop(0)
            provisions_to_steal.append(provisions.pop(choice % len(provisions)))

        for card in provisions_to_steal:
            new_game_state.faction_state[self.target_faction].provisions.remove(card)
            new_game_state.faction_state[self.faction].provisions.append(card)
        new_game_state.provisions_to_return = real_number
        new_game_state.provisions_to_return_faction = self.target_faction
        discard_author(new_game_state, self.faction)
        new_game_state.faction_state[self.faction].used_faction_author = True
        return new_game_state


class ReturnProvisions(Action):
    name = "return-provisions"
    ck_faction = "piglet"
    ck_pause_context = ["steal-provisions"]

    def __init__(self, faction, cards):
        self.faction = faction
        self.cards = cards

    @classmethod
    def parse_args(cls, faction, args):
        cards = args.split(" ")
        return ReturnProvisions(faction, cards)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.ReturnProvisions(game_state.provisions_to_return)

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.provisions_to_return is None:
            raise IllegalAction("You cannot return provisions right now")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        if len(self.cards) != game_state.provisions_to_return:
            raise BadCommand("Did not return the correct number of cards")

        for card in self.cards:
            new_game_state.faction_state[new_game_state.provisions_to_return_faction].provisions.append(card)
            new_game_state.faction_state[self.faction].provisions.remove(card)

        new_game_state.provisions_to_return = None
        new_game_state.provisions_to_return_faction = None
        new_game_state.pause_context = None

        return new_game_state
