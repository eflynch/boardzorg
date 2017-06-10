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

        shuffle(treachery_cards)
        self.treachery_deck = treachery_cards
        self.treachery_discard = []

        spice_cards = SPICE_CARDS[:]
        while spice_cards[0] == "Shai-Hulud":
            shuffle(spice_cards)
        self.spice_deck = spice_cards
        self.spice_discard = []

        self.faction_state = {f: FactionState.from_name(f) for f in factions_playing}
        self.round_state = SetupRound()
        self.alliances = {f: [] for f in factions_playing}
        self.turn = 1
        self.storm_position = 0
        self.storm_advance = 0
        self.shield_wall = True
        self.map_state = {s[0]: SpaceState(*s) for s in SPACES}
        if "atreides" in factions_playing:
            self.map_state["Arrakeen"].forces["atreides"] = {9: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
        if "harkonnen" in factions_playing:
            self.map_state["Carthag"].forces["harkonnen"] = {10: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}
        if "guild" in factions_playing:
            self.map_state["Tueks-Sietch"].forces["guild"] = {4: [1, 1, 1, 1, 1]}

    def assert_valid(self):
        for state in self.faction_state.values():
            state.assert_valid()
        self.round_state.assert_valid()

    def visible(self, faction):
        visible = super().visible(self, faction)
        visible["treachery_deck"] = {"length": len(self.treachery_deck)}
        visible["treachery_discard"] = self.treachery_discard

        visible["spice_deck"] = {"length": len(self.spice_deck)}
        if faction == "atreides" and self.spice_deck:
            visible["spice_deck"]["next"] = self.spice_deck[0]
        visible["spice_discard"] = self.spice_discard

        visible["faction_state"] = {
            f: self.faction_state[f].visible(self, faction)
            for f in self.faction_state
        }

        visible["round_state"] = self.round_state.visible(self, faction)

        visible["alliances"] = self.alliances
        visible["turn"] = self.turn
        visible["shield_wall"] = self.shield_wall
        visible["storm_position"] = self.storm_position

        if faction == "fremen":
            visible["storm_advance"] = self.storm_advance

        visible["map_state"] = {
            s: self.map_state[s].visible(self, faction) for s in self.map_state
        }

        return visible
