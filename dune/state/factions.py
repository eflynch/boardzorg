from dune.state import State
from dune.state.leaders import LEADERS


class FactionState(State):
    ALL_FACTIONS = ["atreides", "emperor", "guild", "fremen", "bene-gesserit", "harkonnen"]

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

    @staticmethod
    def from_name(faction):
        return {
            "atreides": AtreidesState,
            "guild": GuildState,
            "emperor": EmperorState,
            "fremen": FremenState,
            "bene-gesserit": BeneGesseritState,
            "harkonnen": HarkonnenState
        }[faction]()


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
