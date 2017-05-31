from random import shuffle

from state.leader import LEADERS
from state.treachery import TREACHERY_CARDS
from state.space import SPACES, SpaceState
from state.spice import SPICE_CARDS
from factions import FACTIONS


class FactionState:
    def __init__(self):
        self.leaders = LEADERS[self.name][:]
        self.treachery = []
        self.traitors = []
        self.rejected_traitors = []
        self.leader_death_count = {}
        self.tank_leaders = []
        self.tank_units = []
        self.bribe_spice = 0
        self.token_position = None

    def assert_valid(self):
        assert len(self.leaders) + len(self.tank_leaders) == 5
        assert len(self.treachery) <= 4
        assert len(self.traitors) <= 4
        assert self.spice >= 0
        assert self.bribe_spice >= 0


class AtreidesState(FactionState):
    def __init__(self):
        self.name = "atreides"
        super().__init__()
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.spice = 10
        self.units_lost = 0
        self.kwizatz_haderach_available = False
        self.kwizatz_haderach_tanks = False


class GuildState(FactionState):
    def __init__(self):
        self.name = "guild"
        super().__init__()
        self.spice = 5
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


class EmperorState(FactionState):
    def __init__(self):
        self.name = "emperor"
        super().__init__()
        self.spice = 10
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]


class BeneGesseritState(FactionState):
    def __init__(self):
        self.name = "bene-gesserit"
        super().__init__()
        self.prediction = (None, 0)
        self.spice = 5
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


class HarkonnenState(FactionState):
    def __init__(self):
        self.name = "harkonnen"
        super().__init__()
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.spice = 10

    def assert_valid(self):
        assert len(self.leaders) + len(self.tank_leaders) == 5
        assert len(self.treachery) <= 8
        assert len(self.traitors) <= 4
        assert self.spice >= 0
        assert self.bribe_spice >= 0


class FremenState(FactionState):
    def __init__(self):
        self.name = "fremen"
        super().__init__()
        self.spice = 3
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]


class RoundState:
    def assert_valid(self):
        pass


class SetupState(RoundState):
    def __init__(self):
        self.round = "setup"


class StormState(RoundState):
    def __init__(self):
        self.round = "storm"


class SpiceState(RoundState):
    def __init__(self):
        self.round = "spice"


class NexusState(RoundState):
    def __init__(self):
        self.round = "nexus"
        self.proposals = {}
        self.proposals_done = False
        self.worm_done = False
        self.karama_done = False
        self.karama_passes = []


class BiddingState(RoundState):
    def __init__(self):
        self.round = "bidding"
        self.bene_gesserit_charity_claimed = False
        self.faction_turn = None
        self.total_for_auction = 0
        self.up_for_auction = []
        self.bids = {}
        self.payment_done = False
        self.payment_cancel_passed = False
        self.winner = None
        self.prescience_cancel_karama = False
        self.extra_card_karama_used = False
        self.karama_pass = []


class RevivalState(RoundState):
    def __init__(self):
        self.round = "revival"
        self.faction_turn = None


class MovementState(RoundState):
    def __init__(self):
        self.round = "movement"
        self.faction_turn = None
        self.block_guild_turn_karama_used = False
        self.block_guild_turn_karama_pass = []


class BattleState(RoundState):
    def __init__(self):
        self.round = "battle"
        self.faction_turn = "atreides"


class CollectionState(RoundState):
    def __init__(self):
        self.round = "collection"
        self.faction_turn = "atreides"


class BoardState:
    def __init__(self):
        self.storm_position = 0
        self.storm_advance = 0
        self.shield_wall = True
        self.map_state = {s[0]: SpaceState(*s) for s in SPACES}
        self.shai_hulud = None

    def assert_valid(self):
        pass


class GameState:
    def __init__(self):
        t_cards = TREACHERY_CARDS[:]
        s_cards = SPICE_CARDS[:]
        shuffle(s_cards)
        while s_cards[0] == "Shai-Hulud":
            shuffle(s_cards)
        shuffle(t_cards)
        self.treachery_deck = t_cards
        self.spice_deck = s_cards
        self.spice_discard = []
        self.treachery_discard = []
        self.board_state = BoardState()
        self.faction_state = {
            'atreides': AtreidesState(),
            'guild': GuildState(),
            'bene-gesserit': BeneGesseritState(),
            'emperor': EmperorState(),
            'harkonnen': HarkonnenState(),
            'fremen': FremenState()
        }
        self.round_state = SetupState()
        self.alliances = {f: [] for f in FACTIONS}
        self.turn = 0

    def assert_valid(self):
        for state in self.faction_state.values():
            state.assert_valid()
        self.round_state.assert_valid()
        self.board_state.assert_valid()
