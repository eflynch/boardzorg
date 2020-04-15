from copy import deepcopy
import random

from dune.state.treachery_cards import WORTHLESS
from dune.actions import args
from dune.actions.action import Action
from dune.exceptions import IllegalAction, BadCommand


# For now, always use a worthless card before a karama card
def discard_karama(game_state, faction):
    t_deck = game_state.faction_state[faction].treachery
    k_card = "Karama"
    if faction == "bene-gesserit":
        worthless = [card for card in t_deck if card in WORTHLESS]
        if worthless:
            k_card = worthless[0]

    t_deck.remove(k_card)
    game_state.treachery_discard.insert(0, k_card)


class KaramaStealTreachery(Action):
    name = "karama-steal-treachery"
    ck_karama = True
    ck_faction = "harkonnen"

    def __init__(self, faction, target_faction, number):
        self.faction = faction
        self.target_faction = target_faction
        self.number = number

    @classmethod
    def parse_args(cls, faction, args):
        target_faction, number = args.split(" ")
        return KaramaStealTreachery(faction, target_faction, int(number))

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.Struct(args.Faction(), args.Integer(min=0, max=4, type="Cards"))

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        new_game_state.pause_context = "steal-treachery"
        treachery = new_game_state.faction_state[self.target_faction].treachery[:]

        real_number = min(self.number, len(treachery))

        random.shuffle(treachery)
        for card in treachery[:real_number]:
            new_game_state.faction_state[self.target_faction].treachery.remove(card)
            new_game_state.faction_state[self.faction].treachery.append(card)
        new_game_state.treachery_to_return = real_number
        new_game_state.treachery_to_return_faction = self.target_faction
        discard_karama(new_game_state, self.faction)
        return new_game_state


class ReturnTreachery(Action):
    name = "return-treachery"
    ck_faction = "harkonnen"
    ck_pause_context = ["steal-treachery"]

    def __init__(self, faction, cards):
        self.faction = faction
        self.cards = cards

    @classmethod
    def parse_args(cls, faction, args):
        cards = args.split(" ")
        return ReturnTreachery(faction, cards)

    @classmethod
    def get_arg_spec(cls, faction=None, game_state=None):
        return args.ReturnTreachery(game_state.treachery_to_return)

    @classmethod
    def _check(cls, game_state, faction):
        if game_state.treachery_to_return is None:
            raise IllegalAction("You cannot return treachery right now")

    def _execute(self, game_state):
        new_game_state = deepcopy(game_state)
        if len(self.cards) != game_state.treachery_to_return:
            raise BadCommand("Did not return the correct number of cards")

        for card in self.cards:
            new_game_state.faction_state[new_game_state.treachery_to_return_faction].treachery.append(card)
            new_game_state.faction_state[self.faction].treachery.remove(card)

        new_game_state.treachery_to_return = None
        new_game_state.treachery_to_return_faction = None
        new_game_state.pause_context = None

        return new_game_state
