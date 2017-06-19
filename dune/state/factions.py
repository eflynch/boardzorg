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

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["leaders"] = self.leaders
        visible["leader_death_count"] = self.leader_death_count
        visible["tank_leaders"] = self.tank_leaders
        visible["tank_units"] = self.tank_units
        visible["reserve_units"] = self.reserve_units
        visible["bribe_spice"] = self.bribe_spice
        visible["token_position"] = self.token_position
        visible["name"] = self.name

        if faction == self.name:
            visible["spice"] = self.spice
            visible["treachery"] = self.treachery
            visible["traitors"] = self.traitors
            visible["rejected_traitors"] = self.rejected_traitors

        else:
            if game_state.round == "bidding":
                visible["treachery"] = {"length": len(self.treachery)}

        return visible

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

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["units_lost"] = self.units_lost
        visible["kwizatz_haderach_available"] = self.kwizatz_haderach_available
        visible["kwizatz_haderach_tanks"] = self.kwizatz_haderach_tanks
        return visible


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

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        if faction == self.name:
            visible["prediction"] = self.prediction
        return visible


class HarkonnenState(FactionState):
    def __init__(self):
        self.name = "harkonnen"
        super().__init__()
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.spice = 10


class FremenState(FactionState):
    def __init__(self):
        self.name = "fremen"
        super().__init__()
        self.spice = 3
        self.reserve_units = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
