from state.leader import Leader, LEADERS


class SpiceCard:
    def __init__(self, spice=None, space=None, shai_hulud=False):
        self.spice = spice
        self.space = space
        self.shai_hulud = shai_hulud


class FactionState:
    def __init__(self):
        self.leaders = [Leader(*args) for args in LEADERS[self.name]]
        self.treachery = []
        self.traitors = []
        self.rejected_traitors = []
        self.tank_leaders = []
        self.tank_units = []
        self.bribe_spice = 0
        self.token_position = None

    def assert_valid(self):
        assert len(self.reserve_leaders) + len(self.tank_leaders) == 5
        assert len(self.treachery) <= 4
        assert len(self.traitors) <= 1
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
        assert len(self.reserve_leaders) + len(self.tank_leaders) == 5
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
        self.alliance_stage_over = False
        self.fremen_movement_over = False


class BiddingState(RoundState):
    def __init__(self):
        self.round = "bidding"
        self.bene_gesserit_charity_claimed = False
        self.faction_turn = "atreides"


class RevivalState(RoundState):
    def __init__(self):
        self.round = "revival"
        self.faction_turn = "atreides"


class MovementState(RoundState):
    def __init__(self):
        self.round = "movement"
        self.faction_turn = "atreides"


class BattleState(RoundState):
    def __init__(self):
        self.round = "battle"
        self.faction_turn = "atreides"


class CollectionState(RoundState):
    def __init__(self):
        self.round = "collection"
        self.faction_turn = "atreides"


class SpaceState:
    def __init__(self):
        self.name = "A"
        self.is_stronghold = False
        self.is_rock = False
        self.is_protected_by_shieldwall = False
        self.spice_sector = 0
        self.spice = 0
        self.forces = {}
        self.sectors = [1, 2, 3]


class BoardState:
    def __init__(self):
        self.storm_position = 0
        self.storm_advance = 0
        self.shield_wall = True
        self.map_state = {"A": SpaceState()}
        self.shai_hulud = None

    def assert_valid(self):
        pass


class GameState:
    def __init__(self):
        self.treachery_deck = []
        self.spice_deck = []
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
        self.alliances = {
            'atreides': ['atreides'],
            'guild': ['guild']
        }
        self.turn = 0

    def assert_valid(self):
        for state in self.faction_state.values():
            state.assert_valid()
        self.round_state.assert_valid()
        self.board_state.assert_valid()
