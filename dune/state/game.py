import random

from dune.state import State
from dune.state.treachery_cards import TREACHERY_CARDS, WORTHLESS, WEAPONS, DEFENSES
from dune.state.spaces import SPACES, SpaceState
from dune.state.spice_cards import SPICE_CARDS
from dune.state.rounds.setup import SetupRound
from dune.state.factions import FactionState
from dune.state.leaders import LEADERS


class GameState(State):
    @staticmethod
    def new_shuffle(factions=None, treachery_cards=None, seed=None):
        if treachery_cards is None:
            treachery_deck = TREACHERY_CARDS[:]
        else:
            treachery_deck = treachery_cards[:]
        if factions is None:
            factions = FactionState.ALL_FACTIONS

        traitor_deck = []
        for f in factions:
            traitor_deck.extend(LEADERS[f])

        # Introduce Non-Determinism here only
        if seed is not None:
            random.seed(seed)

        spice_deck = SPICE_CARDS[:]
        random.shuffle(spice_deck)
        while spice_deck[0] == "Shai-Hulud":
            random.shuffle(spice_deck)

        random.shuffle(treachery_deck)
        random.shuffle(traitor_deck)
        storm_deck = [random.randint(1, 6) for i in range(20)]
        storm_deck.insert(0, random.randint(0, 17))

        return GameState(factions, treachery_deck, spice_deck, traitor_deck, storm_deck)

    def __init__(self, factions, treachery_deck, spice_deck, traitor_deck, storm_deck):
        self.factions = factions
        self.treachery_deck = treachery_deck
        self.spice_deck = spice_deck
        self.traitor_deck = traitor_deck
        self.storm_deck = storm_deck
        self.spice_discard = []
        self.treachery_discard = []
        self.pause = []

        self.treachery_reference = {
            "worthless": WORTHLESS,
            "weapons": WEAPONS,
            "defenses": DEFENSES
        }

        self.faction_state = {f: FactionState.from_name(f) for f in factions}
        self._round_state = SetupRound()
        self._round = None
        self.alliances = {f: [] for f in factions}
        self.turn = 1
        self.storm_position = 0
        self.shield_wall = True
        self.ornithopters = ["atreides", "harkonnen"]
        self.map_state = {s[0]: SpaceState(*s) for s in SPACES}
        if "atreides" in factions:
            self.map_state["Arrakeen"].forces["atreides"] = {9: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
        if "harkonnen" in factions:
            self.map_state["Carthag"].forces["harkonnen"] = {10: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
        if "guild" in factions:
            self.map_state["Tueks-Sietch"].forces["guild"] = {4: [1, 1, 1, 1, 1]}

        self.winner = None
        self.shai_hulud = None

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
        visible["treachery_deck"] = {"length": len(self.treachery_deck)}
        visible["treachery_discard"] = self.treachery_discard
        visible["treachery_reference"] = self.treachery_reference

        visible["spice_deck"] = {"length": len(self.spice_deck)}
        if faction == "atreides" and self.spice_deck:
            visible["spice_deck"]["next"] = self.spice_deck[0]
        visible["spice_discard"] = self.spice_discard

        visible["faction_state"] = {
            f: self.faction_state[f].visible(self, faction)
            for f in self.faction_state
        }

        if self.round_state is not None:
            visible["round_state"] = self._round_state.visible(self, faction)
        else:
            visible["round_state"] = self.round

        visible["alliances"] = [list(a) for a in self.alliances]
        visible["turn"] = self.turn
        visible["shield_wall"] = self.shield_wall
        visible["storm_position"] = self.storm_position
        visible["storm_deck"] = {"length": len(self.storm_deck)}
        visible["ornithopters"] = self.ornithopters

        if faction == "fremen":
            visible["storm_deck"]["next"] = self.storm_deck[0]

        visible["map_state"] = [self.map_state[s].visible(self, faction) for s in self.map_state]
        visible["winner"] = self.winner
        visible["shai_hulud"] = self.shai_hulud

        return visible
