from boardzorg.state import State
from boardzorg.state.characters import CHARACTERS


class FactionState(State):
    ALL_FACTIONS = ["owl", "eeyore", "kanga", "christopher_robbin", "rabbit", "piglet"]

    def __init__(self):
        self.characters = CHARACTERS[self.name][:]
        self.characters_captured = []
        self.provisions = []
        self.traitors = []
        self.rejected_traitors = []
        self.character_death_count = {}
        self.lost_characters = []
        self.lost_minions = []
        self.bribe_hunny = 0
        self.used_faction_author = False
        self.token_position = None

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["characters"] = self.characters
        visible["characters_captured"] = self.characters_captured
        visible["character_death_count"] = self.character_death_count
        visible["lost_characters"] = self.lost_characters
        visible["lost_minions"] = self.lost_minions
        visible["reserve_minions"] = self.reserve_minions
        visible["bribe_hunny"] = self.bribe_hunny
        visible["token_position"] = self.token_position
        visible["name"] = self.name

        if faction == self.name:
            visible["hunny"] = self.hunny
            visible["provisions"] = self.provisions
            visible["traitors"] = self.traitors
            visible["rejected_traitors"] = self.rejected_traitors

        else:
            if game_state.round == "bidding":
                visible["provisions"] = {"length": len(self.provisions)}

        return visible

    @staticmethod
    def from_name(faction):
        return {
            "owl": OwlState,
            "kanga": KangaState,
            "eeyore": EeyoreState,
            "christopher_robbin": ChristopherRobbinState,
            "rabbit": RabbitState,
            "piglet": PigletState
        }[faction]()


class OwlState(FactionState):
    def __init__(self):
        self.name = "owl"
        super().__init__()
        self.reserve_minions = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.hunny = 10
        self.minions_lost = 0
        self.winnie_the_pooh_available = False

        # Note that the Kwisatz Haderach interacts somewhat strangely with the other lost characters
        # If winnie_the_pooh_losts is "None", the Kwisatz Haderach is not in the losts.
        # If this is a number, that is the death count all other characters must exceed before
        # the Kwisatz Haderach can be revived.
        self.winnie_the_pooh_losts = None


    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        visible["minions_lost"] = self.minions_lost
        visible["winnie_the_pooh_available"] = self.winnie_the_pooh_available
        visible["winnie_the_pooh_losts"] = self.winnie_the_pooh_losts
        return visible


class KangaState(FactionState):
    def __init__(self):
        self.name = "kanga"
        super().__init__()
        self.hunny = 5
        self.reserve_minions = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


class EeyoreState(FactionState):
    def __init__(self):
        self.name = "eeyore"
        super().__init__()
        self.hunny = 10
        self.reserve_minions = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]


class RabbitState(FactionState):
    def __init__(self):
        self.name = "rabbit"
        super().__init__()
        self.prediction = (None, 0)
        self.hunny = 5
        self.reserve_minions = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    def visible(self, game_state, faction):
        visible = super().visible(game_state, faction)
        if faction == self.name:
            visible["prediction"] = self.prediction
        return visible


class PigletState(FactionState):
    def __init__(self):
        self.name = "piglet"
        super().__init__()
        self.reserve_minions = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.hunny = 10


class ChristopherRobbinState(FactionState):
    def __init__(self):
        self.name = "christopher_robbin"
        super().__init__()
        self.hunny = 3
        self.reserve_minions = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
