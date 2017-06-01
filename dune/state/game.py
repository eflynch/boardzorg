from random import shuffle

from dune.state import State
from dune.state.treachery_cards import TREACHERY_CARDS
from dune.state.spaces import SPACES, SpaceState
from dune.state.spice_cards import SPICE_CARDS
from dune.state.rounds.setup import SetupRound
from dune.state.factions import FactionState


class GameState(State):
    def __init__(self, treachery_cards=None, factions_playing=None):
        if treachery_cards is None:
            treachery_cards = TREACHERY_CARDS[:]
        if factions_playing is None:
            factions_playing = FactionState.ALL_FACTIONS

        spice_cards = SPICE_CARDS[:]
        shuffle(spice_cards)
        while spice_cards[0] == "Shai-Hulud":
            shuffle(spice_cards)
        shuffle(treachery_cards)

        self.treachery_deck = treachery_cards
        self.spice_deck = spice_cards
        self.spice_discard = []
        self.treachery_discard = []

        self.faction_state = {f: FactionState.from_name(f) for f in factions_playing}
        self.round_state = SetupRound()
        self.alliances = {f: [] for f in factions_playing}
        self.turn = 1
        self.storm_position = 0
        self.storm_advance = 0
        self.shield_wall = True
        self.map_state = {s[0]: SpaceState(*s) for s in SPACES}

    def assert_valid(self):
        for state in self.faction_state.values():
            state.assert_valid()
        self.round_state.assert_valid()
