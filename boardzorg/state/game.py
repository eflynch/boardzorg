import random
import math

from boardzorg.state import State
from boardzorg.state.provisions_cards import PROVISIONS_CARDS, WORTHLESS, WEAPONS, DEFENSES
from boardzorg.state.spaces import SPACES, SpaceState
from boardzorg.state.hunny_cards import HUNNY_CARDS
from boardzorg.state.rounds.setup import SetupRound
from boardzorg.state.factions import FactionState
from boardzorg.state.characters import CHARACTERS

MAX_CHOICE_SIZE = 5


class GameState(State):
    @staticmethod
    def new_shuffle(factions=None, provisions_cards=None, seed=None):
        if provisions_cards is None:
            provisions_deck = PROVISIONS_CARDS[:]
        else:
            provisions_deck = provisions_cards[:]
        if factions is None:
            factions = FactionState.ALL_FACTIONS

        traitor_deck = []
        for f in factions:
            traitor_deck.extend(CHARACTERS[f])

        # Introduce Non-Determinism here only
        if seed is not None:
            random.seed(seed)

        hunny_deck = HUNNY_CARDS[:]
        random.shuffle(hunny_deck)
        while hunny_deck[0] == "Heffalump":
            random.shuffle(hunny_deck)

        random.shuffle(provisions_deck)
        random.shuffle(traitor_deck)
        bees_deck = [random.randint(1, 6) for i in range(20)]
        bees_deck.insert(0, random.randint(0, 17))

        random_choice_deck = [random.randint(0, math.factorial(MAX_CHOICE_SIZE)) for i in range(50)]

        return GameState(
            factions, provisions_deck, hunny_deck, traitor_deck, bees_deck, random_choice_deck)

    def __init__(self, factions, provisions_deck, hunny_deck, traitor_deck, bees_deck,
                 random_choice_deck=None):
        self.factions = factions
        self.provisions_deck = provisions_deck
        self.hunny_deck = hunny_deck
        self.traitor_deck = traitor_deck
        self.bees_deck = bees_deck
        if not random_choice_deck:
            random_choice_deck = [random.randint(0, math.factorial(MAX_CHOICE_SIZE)) for i in range(50)]
        self.random_choice_deck = random_choice_deck
        self.hunny_discard = []
        self.provisions_discard = []
        self.pause = []
        self.pause_context = None
        self.author_context = {f: None for f in factions}

        self.hunny_context = {f: None for f in factions}
        self.hunny_reserve = {f: None for f in factions}

        self.provisions_to_return = None
        self.provisions_to_return_faction = None

        self.query_flip_to_frends_and_raletions = None
        self.query_flip_to_fighters = None

        self.provisions_reference = {
            "worthless": WORTHLESS,
            "weapons": WEAPONS,
            "defenses": DEFENSES
        }

        self.faction_state = {f: FactionState.from_name(f) for f in factions}
        self._round_state = SetupRound()
        self._round = None
        self.alliances = {f: set([]) for f in factions}
        self.turn = 1
        self.bees_position = 0
        self.umbrella_wall = True
        self.balloons = ["owl", "piglet"]
        self.map_state = {s[0]: SpaceState(*s) for s in SPACES}
        if "owl" in factions:
            self.map_state["OwlsHouse"].forces["owl"] = {9: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
        if "piglet" in factions:
            self.map_state["PigletsHouse"].forces["piglet"] = {10: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
        if "kanga" in factions:
            self.map_state["Kangas-House"].forces["kanga"] = {4: [1, 1, 1, 1, 1]}

        self.winner = None
        self.heffalump = None

    @property
    def round(self):
        if self._round_state is not None:
            return self._round_state.round
        return self._round

    @round.setter
    def round(self, new_round):
        self._round = new_round
        self._round_state = None

    @property
    def round_state(self):
        return self._round_state

    @round_state.setter
    def round_state(self, new_round_state):
        self._round_state = new_round_state
        self._round = None

    def visible(self, faction):
        visible = super().visible(self, faction)
        visible["provisions_deck"] = {"length": len(self.provisions_deck)}
        visible["provisions_discard"] = self.provisions_discard
        visible["provisions_reference"] = self.provisions_reference

        visible["hunny_deck"] = {"length": len(self.hunny_deck)}
        if faction == "owl" and self.hunny_deck:
            visible["hunny_deck"]["next"] = self.hunny_deck[0]
        visible["hunny_discard"] = self.hunny_discard

        visible["faction_state"] = {
            f: self.faction_state[f].visible(self, faction)
            for f in self.faction_state
        }

        if self.round_state is not None:
            visible["round_state"] = self._round_state.visible(self, faction)
        else:
            visible["round_state"] = self.round

        visible_alliances = []
        for a in self.alliances:
            visible_alliances.append(tuple(sorted(self.alliances[a] | set([a]))))

        visible["alliances"] = list(set(visible_alliances))
        visible["turn"] = self.turn
        visible["umbrella_wall"] = self.umbrella_wall
        visible["bees_position"] = self.bees_position
        visible["bees_deck"] = {"length": len(self.bees_deck)}
        visible["balloons"] = self.balloons

        if faction == "christopher_robbin" or self.round == "control":
            visible["bees_deck"]["next"] = self.bees_deck[0]

        visible["map_state"] = [self.map_state[s].visible(self, faction) for s in self.map_state]
        visible["winner"] = self.winner
        visible["heffalump"] = self.heffalump

        return visible
